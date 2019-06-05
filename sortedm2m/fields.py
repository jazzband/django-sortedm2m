# -*- coding: utf-8 -*-
from django.db import models, transaction, router
from django.db.models import signals, Max, Model
from django.db.models.fields.related import (RECURSIVE_RELATIONSHIP_CONSTANT, lazy_related_operation,
                                             ManyToManyField as _ManyToManyField)
from django.db.models.fields.related_descriptors import create_forward_many_to_many_manager, ManyToManyDescriptor
from django.utils.functional import cached_property, curry

from .forms import SortedMultipleChoiceField

SORT_VALUE_FIELD_NAME = 'sort_value'


def add_lazy_relation(cls, field, relation, operation):
    # Rearrange args for new Apps.lazy_model_operation
    def function(local, related, field):
        return operation(field, related, local)

    lazy_related_operation(function, cls, relation, field=field)


def get_foreignkey_field_kwargs(field):
    return {
        'db_tablespace': field.db_tablespace,
        'db_constraint': field.remote_field.db_constraint,
        'on_delete': models.CASCADE,
    }


def create_sorted_many_related_manager(superclass, rel, *args, **kwargs):
    RelatedManager = create_forward_many_to_many_manager(
        superclass, rel, *args, **kwargs)

    class SortedRelatedManager(RelatedManager):
        def get_queryset(self):
            # We use ``extra`` method here because we have no other access to
            # the extra sorting field of the intermediary model. The fields
            # are hidden for joins because we set ``auto_created`` on the
            # intermediary's meta options.
            try:
                return self.instance._prefetched_objects_cache[self.prefetch_cache_name]
            except (AttributeError, KeyError):
                return super(SortedRelatedManager, self).get_queryset().extra(order_by=['%s.%s' % (
                    rel.through._meta.db_table,
                    rel.through._sort_field_name,
                )])

        get_query_set = get_queryset

        def get_prefetch_queryset(self, instances, queryset=None):
            result = super(SortedRelatedManager, self).get_prefetch_queryset(instances, queryset)
            queryset = result[0]
            queryset.query.extra_order_by = [
                '%s.%s' % (rel.through._meta.db_table, rel.through._sort_field_name)]
            return (queryset,) + result[1:]

        get_prefetch_query_set = get_prefetch_queryset

        def set(self, objs, **kwargs):
            # Choosing to clear first will ensure the order is maintained.
            kwargs['clear'] = True
            super(SortedRelatedManager, self).set(objs, **kwargs)

        set.alters_data = True

        def _add_items(self, source_field_name, target_field_name, *objs, **kwargs):
            # source_field_name: the PK fieldname in join table for the source object
            # target_field_name: the PK fieldname in join table for the target object
            # *objs - objects to add. Either object instances, or primary keys of object instances.
            through_defaults = kwargs.get('through_defaults') or {}

            if objs:
                # Django uses a set here, we need to use a list to keep the
                # correct ordering.
                new_ids = []
                for obj in objs:
                    if isinstance(obj, self.model):
                        if not router.allow_relation(obj, self.instance):
                            raise ValueError(
                                'Cannot add "%r": instance is on database "%s", value is on database "%s"' %
                                (obj, self.instance._state.db, obj._state.db)
                            )
                        fk_val = self.through._meta.get_field(target_field_name).get_foreign_related_value(obj)[0]
                        if fk_val is None:
                            raise ValueError('Cannot add "%r": the value for field "%s" is None' %
                                             (obj, target_field_name))
                        new_ids.append(fk_val)
                    elif isinstance(obj, Model):
                        raise TypeError(
                            "'%s' instance expected, got %r" % (self.model._meta.object_name, obj)
                        )
                    else:
                        new_ids.append(obj)

                db = router.db_for_write(self.through, instance=self.instance)
                manager = self.through._default_manager.using(db)
                params = {source_field_name: self.related_val[0], '%s__in' % target_field_name: new_ids}
                vals = set(self.through._default_manager.using(db).filter(**params)
                           .values_list(target_field_name, flat=True))

                new_ids_set = set(new_ids)
                new_ids_set.difference_update(vals)
                new_ids = [_id for _id in new_ids if _id in new_ids_set]

                if self.reverse or source_field_name == self.source_field_name:
                    # Don't send the signal when we are inserting the
                    # duplicate data row for symmetrical reverse entries.
                    signals.m2m_changed.send(sender=rel.through, action='pre_add',
                                             instance=self.instance, reverse=self.reverse,
                                             model=self.model, pk_set=new_ids_set, using=db)

                # Add the ones that aren't there already
                with transaction.atomic(using=db):
                    if self.reverse or source_field_name == self.source_field_name:
                        signals.m2m_changed.send(
                            sender=rel.through, action='pre_add', instance=self.instance,
                            reverse=self.reverse, model=self.model, pk_set=new_ids_set, using=db
                        )

                    rel_source_fk = self.related_val[0]
                    sort_field_name = self.through._sort_field_name
                    source_queryset = manager.filter(**{'%s_id' % source_field_name: rel_source_fk})
                    sort_value_max = source_queryset.aggregate(max=Max(sort_field_name))['max'] or 0

                    bulk_data = [
                        {**through_defaults, **{
                            '%s_id' % source_field_name: rel_source_fk,
                            '%s_id' % target_field_name: obj_id,
                            sort_field_name: i,
                        }} for i, obj_id in enumerate(new_ids, sort_value_max + 1)
                    ]

                    manager.bulk_create([self.through(**data) for data in bulk_data])

                    if self.reverse or source_field_name == self.source_field_name:
                        # Don't send the signal when we are inserting the
                        # duplicate data row for symmetrical reverse entries.
                        signals.m2m_changed.send(
                            sender=rel.through, action='post_add', instance=self.instance,
                            reverse=self.reverse, model=self.model, pk_set=new_ids_set, using=db
                        )

    return SortedRelatedManager


class SortedManyToManyDescriptor(ManyToManyDescriptor):
    def __init__(self, field):
        super(SortedManyToManyDescriptor, self).__init__(field.remote_field)

    @cached_property
    def related_manager_cls(self):
        model = self.rel.model
        return create_sorted_many_related_manager(model._default_manager.__class__, self.rel, reverse=False)


class SortedManyToManyField(_ManyToManyField):
    """
    Providing a many to many relation that remembers the order of related
    objects.

    Accept a boolean ``sorted`` attribute which specifies if relation is
    ordered or not. Default is set to ``True``. If ``sorted`` is set to
    ``False`` the field will behave exactly like django's ``ManyToManyField``.

    Accept a class ``base_class`` attribute which specifies the base class of
    the intermediate model. It allows to customize the intermediate model.
    """

    def __init__(self, to, sorted=True, base_class=None, **kwargs):
        self.sorted = sorted
        self.sort_value_field_name = kwargs.pop('sort_value_field_name', SORT_VALUE_FIELD_NAME)

        # Base class of through model
        self.base_class = base_class

        super(SortedManyToManyField, self).__init__(to, **kwargs)
        if self.sorted:
            self.help_text = kwargs.get('help_text', None)

    def deconstruct(self):
        # We have to persist custom added options in the ``kwargs``
        # dictionary. For readability only non-default values are stored.
        name, path, args, kwargs = super(SortedManyToManyField, self).deconstruct()
        if self.sort_value_field_name is not SORT_VALUE_FIELD_NAME:
            kwargs['sort_value_field_name'] = self.sort_value_field_name
        if self.sorted is not True:
            kwargs['sorted'] = self.sorted
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, **kwargs):
        if not self.sorted:
            return super(SortedManyToManyField, self).contribute_to_class(cls, name, **kwargs)

        # To support multiple relations to self, it's useful to have a non-None
        # related name on symmetrical relations for internal reasons. The
        # concept doesn't make a lot of sense externally ("you want me to
        # specify *what* on my non-reversible relation?!"), so we set it up
        # automatically. The funky name reduces the chance of an accidental
        # clash.
        rel = self.remote_field
        rel_to = rel.model
        if rel.symmetrical and (rel_to == "self" or rel_to == cls._meta.object_name):
            rel.related_name = "%s_rel_+" % name

        super(_ManyToManyField, self).contribute_to_class(cls, name, **kwargs)

        # The intermediate m2m model is not auto created if:
        #  1) There is a manually specified intermediate, or
        #  2) The class owning the m2m field is abstract.
        if not rel.through and not cls._meta.abstract:
            rel.through = self.create_intermediate_model(cls)

        # Add the descriptor for the m2m relation
        setattr(cls, self.name, SortedManyToManyDescriptor(self))

        # Set up the accessor for the m2m table name for the relation
        self.m2m_db_table = curry(self._get_m2m_db_table, cls._meta)

        # Populate some necessary rel arguments so that cross-app relations
        # work correctly.
        if isinstance(rel.through, str):
            def resolve_through_model(field, model, cls):
                field.remote_field.through = model

            add_lazy_relation(cls, self, rel.through, resolve_through_model)

    def get_internal_type(self):
        return 'ManyToManyField'

    def formfield(self, **kwargs):
        defaults = {}
        if self.sorted:
            defaults['form_class'] = SortedMultipleChoiceField
        defaults.update(kwargs)
        return super(SortedManyToManyField, self).formfield(**defaults)

    ###############################
    # Intermediate Model Creation #
    ###############################

    def get_intermediate_model_name(self, klass):
        return '%s_%s' % (klass._meta.object_name, self.name)

    def get_intermediate_model_meta_class(self, klass, from_field_name, to_field_name, sort_value_field_name):
        managed = True
        to_model = self.remote_field.model
        if isinstance(to_model, str):
            if to_model != RECURSIVE_RELATIONSHIP_CONSTANT:
                def set_managed(field, model, cls):
                    field.remote_field.through._meta.managed = model._meta.managed or cls._meta.managed

                add_lazy_relation(klass, self, to_model, set_managed)
            else:
                managed = klass._meta.managed
        else:
            managed = klass._meta.managed or to_model._meta.managed

        options = {
            'db_table': self._get_m2m_db_table(klass._meta),
            'managed': managed,
            'auto_created': klass,
            'app_label': klass._meta.app_label,
            'db_tablespace': klass._meta.db_tablespace,
            'unique_together': ((from_field_name, to_field_name),),
            'ordering': (sort_value_field_name,),
            'verbose_name': '%(from)s-%(to)s relationship' % {'from': from_field_name, 'to': to_field_name},
            'verbose_name_plural': '%(from)s-%(to)s relationships' % {'from': from_field_name, 'to': to_field_name},
            'apps': self.model._meta.apps,
        }
        return type(str('Meta'), (object,), options)

    def get_rel_to_model_and_object_name(self, klass):
        rel_to = self.remote_field.model
        if isinstance(rel_to, str):
            if rel_to != RECURSIVE_RELATIONSHIP_CONSTANT:
                to_model = rel_to
                to_object_name = to_model.split('.')[-1]
            else:
                to_model = klass
                to_object_name = to_model._meta.object_name
        else:
            to_model = rel_to
            to_object_name = to_model._meta.object_name
        return to_model, to_object_name

    def get_intermediate_model_sort_value_field(self, klass):
        field_name = self.sort_value_field_name
        field = models.IntegerField(default=0)
        return field_name, field

    def get_intermediate_model_from_field(self, klass):
        name = self.get_intermediate_model_name(klass)
        to_model, to_object_name = self.get_rel_to_model_and_object_name(klass)

        if self.remote_field.model == RECURSIVE_RELATIONSHIP_CONSTANT or to_object_name == klass._meta.object_name:
            field_name = 'from_%s' % to_object_name.lower()
        else:
            field_name = klass._meta.model_name

        field = models.ForeignKey(klass, related_name='%s+' % name, **get_foreignkey_field_kwargs(self))
        return field_name, field

    def get_intermediate_model_to_field(self, klass):
        name = self.get_intermediate_model_name(klass)
        to_model, to_object_name = self.get_rel_to_model_and_object_name(klass)

        if self.remote_field.model == RECURSIVE_RELATIONSHIP_CONSTANT or to_object_name == klass._meta.object_name:
            field_name = 'to_%s' % to_object_name.lower()
        else:
            field_name = to_object_name.lower()

        field = models.ForeignKey(to_model, related_name='%s+' % name, **get_foreignkey_field_kwargs(self))
        return field_name, field

    def create_intermediate_model_from_attrs(self, klass, attrs):
        name = self.get_intermediate_model_name(klass)
        base_classes = (self.base_class, models.Model) if self.base_class else (models.Model,)
        return type(str(name), base_classes, attrs)

    def create_intermediate_model(self, klass):
        # Construct and return the new class.
        from_field_name, from_field = self.get_intermediate_model_from_field(klass)
        to_field_name, to_field = self.get_intermediate_model_to_field(klass)
        sort_value_field_name, sort_value_field = self.get_intermediate_model_sort_value_field(klass)
        meta = self.get_intermediate_model_meta_class(klass, from_field_name, to_field_name, sort_value_field_name)

        attrs = {
            'Meta': meta,
            '__module__': klass.__module__,
            from_field_name: from_field,
            to_field_name: to_field,
            sort_value_field_name: sort_value_field,
            '_sort_field_name': sort_value_field_name,
            '_from_field_name': from_field_name,
            '_to_field_name': to_field_name,
        }
        return self.create_intermediate_model_from_attrs(klass, attrs)
