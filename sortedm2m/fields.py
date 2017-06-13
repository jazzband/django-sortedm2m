# -*- coding: utf-8 -*-
import django
from django.conf import settings
from django.db import router
from django.db import transaction
from django.db import models
from django.db.models import signals
from django.db.models.fields.related import ManyToManyField as _ManyToManyField
from django.db.models.fields.related import RECURSIVE_RELATIONSHIP_CONSTANT
from django.utils import six
from django.utils.functional import cached_property, curry

from .compat import create_forward_many_to_many_manager
from .compat import get_foreignkey_field_kwargs
from .compat import get_model_name, get_rel, get_rel_to, add_lazy_relation
from .forms import SortedMultipleChoiceField

SORT_VALUE_FIELD_NAME = 'sort_value'


if hasattr(transaction, 'atomic'):
    atomic = transaction.atomic
# Django 1.5 support
# We mock the atomic context manager.
else:
    class atomic(object):
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass


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
                # Django 1.5 support.
                if not hasattr(RelatedManager, 'get_queryset'):
                    queryset = super(SortedRelatedManager, self).get_query_set()
                else:
                    queryset = super(SortedRelatedManager, self).get_queryset()
                return queryset.extra(order_by=['%s.%s' % (
                    rel.through._meta.db_table,
                    rel.through._sort_field_name,
                )])

        get_query_set = get_queryset

        if not hasattr(RelatedManager, '_get_fk_val'):
            @property
            def _fk_val(self):
                # Django 1.5 support.
                if not hasattr(self, 'related_val'):
                    return self._pk_val
                return self.related_val[0]

        def get_prefetch_queryset(self, instances, queryset=None):
            # Django 1.5 support. The method name changed since.
            if django.VERSION < (1, 6):
                result = super(SortedRelatedManager, self).get_prefetch_query_set(instances)
            # Django 1.6 support. The queryset parameter was not supported.
            elif django.VERSION < (1, 7):
                result = super(SortedRelatedManager, self).get_prefetch_queryset(instances)
            else:
                result = super(SortedRelatedManager, self).get_prefetch_queryset(instances, queryset)
            queryset = result[0]
            queryset.query.extra_order_by = [
                '%s.%s' % (
                    rel.through._meta.db_table,
                    rel.through._sort_field_name,
                )]
            return (queryset,) + result[1:]

        get_prefetch_query_set = get_prefetch_queryset

        def set(self, objs, **kwargs):
            # Choosing to clear first will ensure the order is maintained.
            kwargs['clear'] = True
            super(SortedRelatedManager, self).set(objs, **kwargs)
        set.alters_data = True

        def _add_items(self, source_field_name, target_field_name, *objs):
            # source_field_name: the PK fieldname in join table for the source object
            # target_field_name: the PK fieldname in join table for the target object
            # *objs - objects to add. Either object instances, or primary keys of object instances.

            # If there aren't any objects, there is nothing to do.
            from django.db.models import Max, Model
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
                        if hasattr(self, '_get_fk_val'):  # Django>=1.5
                            fk_val = self._get_fk_val(obj, target_field_name)
                            if fk_val is None:
                                raise ValueError('Cannot add "%r": the value for field "%s" is None' %
                                                 (obj, target_field_name))
                            new_ids.append(self._get_fk_val(obj, target_field_name))
                        else:  # Django<1.5
                            new_ids.append(obj.pk)
                    elif isinstance(obj, Model):
                        raise TypeError(
                            "'%s' instance expected, got %r" %
                            (self.model._meta.object_name, obj)
                        )
                    else:
                        new_ids.append(obj)

                db = router.db_for_write(self.through, instance=self.instance)
                manager = self.through._default_manager.using(db)
                vals = (manager
                        .values_list(target_field_name, flat=True)
                        .filter(**{
                            source_field_name: self._fk_val,
                            '%s__in' % target_field_name: new_ids,
                        }))
                for val in vals:
                    if val in new_ids:
                        new_ids.remove(val)
                _new_ids = []
                for pk in new_ids:
                    if pk not in _new_ids:
                        _new_ids.append(pk)
                new_ids = _new_ids
                new_ids_set = set(new_ids)

                if self.reverse or source_field_name == self.source_field_name:
                    # Don't send the signal when we are inserting the
                    # duplicate data row for symmetrical reverse entries.
                    signals.m2m_changed.send(sender=rel.through, action='pre_add',
                        instance=self.instance, reverse=self.reverse,
                        model=self.model, pk_set=new_ids_set, using=db)

                # Add the ones that aren't there already
                with atomic(using=db):
                    fk_val = self._fk_val
                    source_queryset = manager.filter(**{'%s_id' % source_field_name: fk_val})
                    sort_field_name = self.through._sort_field_name
                    sort_value_max = source_queryset.aggregate(max=Max(sort_field_name))['max'] or 0

                    manager.bulk_create([
                        self.through(**{
                            '%s_id' % source_field_name: fk_val,
                            '%s_id' % target_field_name: pk,
                            sort_field_name: sort_value_max + i + 1,
                        })
                        for i, pk in enumerate(new_ids)
                    ])

                if self.reverse or source_field_name == self.source_field_name:
                    # Don't send the signal when we are inserting the
                    # duplicate data row for symmetrical reverse entries.
                    signals.m2m_changed.send(sender=rel.through, action='post_add',
                        instance=self.instance, reverse=self.reverse,
                        model=self.model, pk_set=new_ids_set, using=db)

    return SortedRelatedManager


try:
    from django.db.models.fields.related_descriptors import ManyToManyDescriptor

    class SortedManyToManyDescriptor(ManyToManyDescriptor):
        def __init__(self, field):
            super(SortedManyToManyDescriptor, self).__init__(field.remote_field)

        @cached_property
        def related_manager_cls(self):
            model = self.rel.model
            return create_sorted_many_related_manager(
                model._default_manager.__class__,
                self.rel,
                # This is the new `reverse` argument (which ironically should
                # be False)
                reverse=False,
            )
except ImportError:
    # Django 1.8 support
    from django.db.models.fields.related import ReverseManyRelatedObjectsDescriptor

    class SortedManyToManyDescriptor(ReverseManyRelatedObjectsDescriptor):
        @cached_property
        def related_manager_cls(self):
            return create_sorted_many_related_manager(
                get_rel_to(self.field)._default_manager.__class__,
                get_rel(self.field))


class SortedManyToManyField(_ManyToManyField):
    '''
    Providing a many to many relation that remembers the order of related
    objects.

    Accept a boolean ``sorted`` attribute which specifies if relation is
    ordered or not. Default is set to ``True``. If ``sorted`` is set to
    ``False`` the field will behave exactly like django's ``ManyToManyField``.

    Accept a class ``base_class`` attribute which specifies the base class of
    the intermediate model. It allows to customize the intermediate model.
    '''
    def __init__(self, to, sorted=True, base_class=None, **kwargs):
        self.sorted = sorted
        self.sort_value_field_name = kwargs.pop(
            'sort_value_field_name',
            SORT_VALUE_FIELD_NAME)

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
        rel = get_rel(self)
        rel_to = get_rel_to(self)
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
        if isinstance(rel.through, six.string_types):
            def resolve_through_model(field, model, cls):
                get_rel(field).through = model
            add_lazy_relation(cls, self, rel.through, resolve_through_model)

        if hasattr(cls._meta, 'duplicate_targets'):  # Django<1.5
            if isinstance(rel_to, six.string_types):
                target = rel_to
            else:
                target = rel_to._meta.db_table
            cls._meta.duplicate_targets[self.column] = (target, "m2m")

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

    def get_intermediate_model_meta_class(self, klass, from_field_name,
                                          to_field_name,
                                          sort_value_field_name):
        managed = True
        to_model = get_rel_to(self)
        if isinstance(to_model, six.string_types):
            if to_model != RECURSIVE_RELATIONSHIP_CONSTANT:
                def set_managed(field, model, cls):
                    get_rel(field).through._meta.managed = model._meta.managed or cls._meta.managed
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
        }
        # Django 1.6 support.
        if hasattr(self.model._meta, 'apps'):
            options.update({
                'apps': self.model._meta.apps,
            })
        return type(str('Meta'), (object,), options)

    def get_rel_to_model_and_object_name(self, klass):
        rel_to = get_rel_to(self)
        if isinstance(rel_to, six.string_types):
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

        if get_rel_to(self) == RECURSIVE_RELATIONSHIP_CONSTANT or to_object_name == klass._meta.object_name:
            field_name = 'from_%s' % to_object_name.lower()
        else:
            field_name = get_model_name(klass)

        field = models.ForeignKey(klass, related_name='%s+' % name,
                                  **get_foreignkey_field_kwargs(self))
        return field_name, field

    def get_intermediate_model_to_field(self, klass):
        name = self.get_intermediate_model_name(klass)

        to_model, to_object_name = self.get_rel_to_model_and_object_name(klass)

        if get_rel_to(self) == RECURSIVE_RELATIONSHIP_CONSTANT or to_object_name == klass._meta.object_name:
            field_name = 'to_%s' % to_object_name.lower()
        else:
            field_name = to_object_name.lower()

        field = models.ForeignKey(to_model, related_name='%s+' % name,
                                  **get_foreignkey_field_kwargs(self))
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
        meta = self.get_intermediate_model_meta_class(klass,
                                                      from_field_name,
                                                      to_field_name,
                                                      sort_value_field_name)

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


# Add introspection rules for South database migrations
# See http://south.aeracode.org/docs/customfields.html
try:
    import south
except ImportError:
    south = None


if south is not None and 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(
        [(
            (SortedManyToManyField,),
            [],
            {"sorted": ["sorted", {"default": True}]},
        )],
        [r'^sortedm2m\.fields\.SortedManyToManyField']
    )

    # Monkeypatch South M2M actions to create the sorted through model.
    # FIXME: This doesn't detect if you changed the sorted argument to the field.
    import south.creator.actions
    from south.creator.freezer import model_key

    class AddM2M(south.creator.actions.AddM2M):
        SORTED_FORWARDS_TEMPLATE = '''
        # Adding SortedM2M table for field %(field_name)s on '%(model_name)s'
        db.create_table(%(table_name)r, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            (%(left_field)r, models.ForeignKey(orm[%(left_model_key)r], null=False)),
            (%(right_field)r, models.ForeignKey(orm[%(right_model_key)r], null=False)),
            (%(sort_field)r, models.IntegerField())
        ))
        db.create_unique(%(table_name)r, [%(left_column)r, %(right_column)r])'''

        def console_line(self):
            if isinstance(self.field, SortedManyToManyField) and self.field.sorted:
                return " + Added SortedM2M table for %s on %s.%s" % (
                    self.field.name,
                    self.model._meta.app_label,
                    self.model._meta.object_name,
                )
            else:
                return super(AddM2M, self).console_line()

        def forwards_code(self):
            if isinstance(self.field, SortedManyToManyField) and self.field.sorted:
                return self.SORTED_FORWARDS_TEMPLATE % {
                    "model_name": self.model._meta.object_name,
                    "field_name": self.field.name,
                    "table_name": self.field.m2m_db_table(),
                    "left_field": self.field.m2m_column_name()[:-3], # Remove the _id part
                    "left_column": self.field.m2m_column_name(),
                    "left_model_key": model_key(self.model),
                    "right_field": self.field.m2m_reverse_name()[:-3], # Remove the _id part
                    "right_column": self.field.m2m_reverse_name(),
                    "right_model_key": model_key(get_rel_to(self.field)),
                    "sort_field": self.field.sort_value_field_name,
                }
            else:
                return super(AddM2M, self).forwards_code()

    class DeleteM2M(AddM2M):
        def console_line(self):
            return " - Deleted M2M table for %s on %s.%s" % (
                self.field.name,
                self.model._meta.app_label,
                self.model._meta.object_name,
            )

        def forwards_code(self):
            return AddM2M.backwards_code(self)

        def backwards_code(self):
            return AddM2M.forwards_code(self)

    south.creator.actions.AddM2M = AddM2M
    south.creator.actions.DeleteM2M = DeleteM2M
