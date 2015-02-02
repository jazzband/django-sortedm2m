# -*- coding: utf-8 -*-
from operator import attrgetter
import sys

import django
from django.conf import settings
from django.db import connections
from django.db import router
from django.db import transaction
from django.db.models import signals
from django.db.models.fields.related import add_lazy_relation, create_many_related_manager, create_many_to_many_intermediary_model
from django.db.models.fields.related import ManyToManyField, ReverseManyRelatedObjectsDescriptor
from django.db.models.fields.related import RECURSIVE_RELATIONSHIP_CONSTANT
from django.utils import six
from django.utils.functional import curry

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


def create_sorted_many_to_many_intermediate_model(field, klass):
    from django.db import models
    managed = True
    if isinstance(field.rel.to, six.string_types) and field.rel.to != RECURSIVE_RELATIONSHIP_CONSTANT:
        to_model = field.rel.to
        to = to_model.split('.')[-1]

        def set_managed(field, model, cls):
            field.rel.through._meta.managed = model._meta.managed or cls._meta.managed
        add_lazy_relation(klass, field, to_model, set_managed)
    elif isinstance(field.rel.to, six.string_types):
        to = klass._meta.object_name
        to_model = klass
        managed = klass._meta.managed
    else:
        to = field.rel.to._meta.object_name
        to_model = field.rel.to
        managed = klass._meta.managed or to_model._meta.managed
    name = '%s_%s' % (klass._meta.object_name, field.name)
    if field.rel.to == RECURSIVE_RELATIONSHIP_CONSTANT or to == klass._meta.object_name:
        from_ = 'from_%s' % to.lower()
        to = 'to_%s' % to.lower()
    else:
        # Django 1.5 support.
        if not hasattr(klass._meta, 'model_name'):
            from_ = klass._meta.object_name.lower()
        else:
            from_ = klass._meta.model_name
        to = to.lower()
    options = {
        'db_table': field._get_m2m_db_table(klass._meta),
        'managed': managed,
        'auto_created': klass,
        'app_label': klass._meta.app_label,
        'db_tablespace': klass._meta.db_tablespace,
        'unique_together': (from_, to),
        'ordering': (field.sort_value_field_name,),
        'verbose_name': '%(from)s-%(to)s relationship' % {'from': from_, 'to': to},
        'verbose_name_plural': '%(from)s-%(to)s relationships' % {'from': from_, 'to': to},
    }
    # Django 1.6 support.
    if hasattr(field.model._meta, 'apps'):
        options.update({
            'apps': field.model._meta.apps,
        })

    meta = type(str('Meta'), (object,), options)
    # Construct and return the new class.
    def default_sort_value(name):
        model = models.get_model(klass._meta.app_label, name)
        # Django 1.5 support.
        if django.VERSION < (1, 6):
            return model._default_manager.count()
        else:
            from django.db.utils import ProgrammingError, OperationalError
            try:
                # We need to catch if the model is not yet migrated in the
                # database. The default function is still called in this case while
                # running the migration. So we mock the return value of 0.
                with transaction.atomic():
                    return model._default_manager.count()
            except (ProgrammingError, OperationalError):
                return 0

    default_sort_value = curry(default_sort_value, name)

    # Django 1.5 support.
    if django.VERSION < (1, 6):
        foreignkey_field_kwargs = {}
    else:
        foreignkey_field_kwargs = dict(
            db_tablespace=field.db_tablespace,
            db_constraint=field.rel.db_constraint)

    return type(str(name), (models.Model,), {
        'Meta': meta,
        '__module__': klass.__module__,
        from_: models.ForeignKey(klass, related_name='%s+' % name, **foreignkey_field_kwargs),
        to: models.ForeignKey(to_model, related_name='%s+' % name, **foreignkey_field_kwargs),
        field.sort_value_field_name: models.IntegerField(default=default_sort_value),
        '_sort_field_name': field.sort_value_field_name,
        '_from_field_name': from_,
        '_to_field_name': to,
    })


def create_sorted_many_related_manager(superclass, rel):
    RelatedManager = create_many_related_manager(superclass, rel)

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

        def _add_items(self, source_field_name, target_field_name, *objs):
            # source_field_name: the PK fieldname in join table for the source object
            # target_field_name: the PK fieldname in join table for the target object
            # *objs - objects to add. Either object instances, or primary keys of object instances.

            # If there aren't any objects, there is nothing to do.
            from django.db.models import Model
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
                vals = (self.through._default_manager.using(db)
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
                sort_field_name = self.through._sort_field_name
                sort_field = self.through._meta.get_field_by_name(sort_field_name)[0]
                if django.VERSION < (1, 6):
                    for obj_id in new_ids:
                        self.through._default_manager.using(db).create(**{
                            '%s_id' % source_field_name: self._fk_val,  # Django 1.5 compatibility
                            '%s_id' % target_field_name: obj_id,
                            sort_field_name: sort_field.get_default(),
                        })
                else:
                    with transaction.atomic():
                        sort_field_default = sort_field.get_default()
                        self.through._default_manager.using(db).bulk_create([
                            self.through(**{
                                '%s_id' % source_field_name: self._fk_val,
                                '%s_id' % target_field_name: v,
                                sort_field_name: sort_field_default + i,
                            })
                            for i, v in enumerate(new_ids)
                        ])                  
                if self.reverse or source_field_name == self.source_field_name:
                    # Don't send the signal when we are inserting the
                    # duplicate data row for symmetrical reverse entries.
                    signals.m2m_changed.send(sender=rel.through, action='post_add',
                        instance=self.instance, reverse=self.reverse,
                        model=self.model, pk_set=new_ids_set, using=db)

    return SortedRelatedManager


class ReverseSortedManyRelatedObjectsDescriptor(ReverseManyRelatedObjectsDescriptor):
    @property
    def related_manager_cls(self):
        return create_sorted_many_related_manager(
            self.field.rel.to._default_manager.__class__,
            self.field.rel
        )


class SortedManyToManyField(ManyToManyField):
    '''
    Providing a many to many relation that remembers the order of related
    objects.

    Accept a boolean ``sorted`` attribute which specifies if relation is
    ordered or not. Default is set to ``True``. If ``sorted`` is set to
    ``False`` the field will behave exactly like django's ``ManyToManyField``.
    '''
    def __init__(self, to, sorted=True, **kwargs):
        self.sorted = sorted
        self.sort_value_field_name = kwargs.pop(
            'sort_value_field_name',
            SORT_VALUE_FIELD_NAME)
        super(SortedManyToManyField, self).__init__(to, **kwargs)
        if self.sorted:
            self.help_text = kwargs.get('help_text', None)

    def contribute_to_class(self, cls, name):
        if not self.sorted:
            return super(SortedManyToManyField, self).contribute_to_class(cls, name)

        # To support multiple relations to self, it's useful to have a non-None
        # related name on symmetrical relations for internal reasons. The
        # concept doesn't make a lot of sense externally ("you want me to
        # specify *what* on my non-reversible relation?!"), so we set it up
        # automatically. The funky name reduces the chance of an accidental
        # clash.
        if self.rel.symmetrical and (self.rel.to == "self" or self.rel.to == cls._meta.object_name):
            self.rel.related_name = "%s_rel_+" % name

        super(ManyToManyField, self).contribute_to_class(cls, name)

        # The intermediate m2m model is not auto created if:
        #  1) There is a manually specified intermediate, or
        #  2) The class owning the m2m field is abstract.
        if not self.rel.through and not cls._meta.abstract:
            self.rel.through = create_sorted_many_to_many_intermediate_model(self, cls)

        # Add the descriptor for the m2m relation
        setattr(cls, self.name, ReverseSortedManyRelatedObjectsDescriptor(self))

        # Set up the accessor for the m2m table name for the relation
        self.m2m_db_table = curry(self._get_m2m_db_table, cls._meta)

        # Populate some necessary rel arguments so that cross-app relations
        # work correctly.
        if isinstance(self.rel.through, six.string_types):
            def resolve_through_model(field, model, cls):
                field.rel.through = model
            add_lazy_relation(cls, self, self.rel.through, resolve_through_model)

        if hasattr(cls._meta, 'duplicate_targets'):  # Django<1.5
            if isinstance(self.rel.to, six.string_types):
                target = self.rel.to
            else:
                target = self.rel.to._meta.db_table
            cls._meta.duplicate_targets[self.column] = (target, "m2m")

    def get_internal_type(self):
        return 'ManyToManyField'

    def formfield(self, **kwargs):
        defaults = {}
        if self.sorted:
            defaults['form_class'] = SortedMultipleChoiceField
        defaults.update(kwargs)
        return super(SortedManyToManyField, self).formfield(**defaults)


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
                    "right_model_key": model_key(self.field.rel.to),
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
