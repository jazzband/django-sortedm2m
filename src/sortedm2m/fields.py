# -*- coding: utf-8 -*-
from django.db import connection, models
from django.db.models.fields.related import create_many_related_manager, ManyToManyField, ReverseManyRelatedObjectsDescriptor
from sortedm2m.forms import SortedMultipleChoiceField


SORT_VALUE_FIELD_NAME = 'sort_value'


def create_sorted_many_related_manager(superclass, field):
    RelatedManager = create_many_related_manager(superclass, field.rel.through)
    class SortedRelatedManager(RelatedManager):
        def get_query_set(self):
            return super(SortedRelatedManager, self).get_query_set().\
                order_by('%s__%s' % (
                    self.m2m_field.rel.through_model.related_name,
                    self.m2m_field.rel.through_model._sort_field_name,
                ))

        def add(self, *objs):
            through = field.rel.through_model
            count = self.m2m_field.rel.through_model._default_manager.count
            for obj in objs:
                through._default_manager.create(**{
                    field.rel.to._meta.object_name.lower(): obj,
                    # using from model's name as field name
                    field.from_model._meta.object_name.lower(): self.instance,
                    through._sort_field_name: count(),
                })
        add.alters_data = True

        def remove(self, *objs):
            through = field.rel.through_model
            for obj in objs:
                through._default_manager.filter(**{
                    '%s__in' % field.rel.to._meta.object_name.lower(): objs,
                    # using from model's name as field name
                    field.from_model._meta.object_name.lower(): self.instance,
                }).delete()
        remove.alters_data = True
    SortedRelatedManager.m2m_field = field
    SortedRelatedManager.from_model = field.from_model
    return SortedRelatedManager


class ReverseSortedManyRelatedObjectsDescriptor(ReverseManyRelatedObjectsDescriptor):
    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        # Dynamically create a class that subclasses the related
        # model's default manager.
        rel_model=self.field.rel.to
        superclass = rel_model._default_manager.__class__
        RelatedManager = create_sorted_many_related_manager(superclass, self.field)

        qn = connection.ops.quote_name
        manager = RelatedManager(
            model=rel_model,
            core_filters={'%s__pk' % self.field.related_query_name(): instance._get_pk_val()},
            instance=instance,
            symmetrical=(self.field.rel.symmetrical and isinstance(instance, rel_model)),
            join_table=qn(self.field.m2m_db_table()),
            source_col_name=qn(self.field.m2m_column_name()),
            target_col_name=qn(self.field.m2m_reverse_name())
        )

        return manager

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError, "Manager must be accessed via instance"

        manager = self.__get__(instance)
        manager.clear()
        manager.add(*value)


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
        if self.sorted:
            # TODO(gregor@muellegger):
            # This is very hacky and should be removed if a better solution is
            # found.
            kwargs.setdefault('through', True)
        super(SortedManyToManyField, self).__init__(to, **kwargs)
        self.help_text = kwargs.get('help_text', None)

    def create_intermediary_model(self, cls, field_name):
        '''
        Create intermediary model that stores the relation's data.
        '''
        module = ''

        # make sure rel.to is a model class and not a string
        if isinstance(self.rel.to, basestring):
            bits = self.rel.to.split('.')
            if len(bits) == 1:
                bits = cls._meta.app_label.lower(), bits[0]
            self.rel.to = models.get_model(*bits)

        model_name = '%s_%s_%s' % (
            cls._meta.app_label,
            cls._meta.object_name,
            field_name)
        from_ = '%s.%s' % (
            cls._meta.app_label,
            cls._meta.object_name)
        related_name = '_%s_%s_%s' % (
            cls._meta.app_label.lower(),
            cls._meta.object_name.lower(),
            field_name.lower(),
        )

        def default_sort_value():
            model = models.get_model(cls._meta.app_label, model_name)
            return model._default_manager.count()

        # Using from and to model's name as field names for relations. This is
        # also django default behaviour for m2m intermediary tables.
        fields = {
            cls._meta.object_name.lower():
                models.ForeignKey(from_, related_name=related_name),
            # using to model's name as field name for the other relation
            self.rel.to._meta.object_name.lower():
                models.ForeignKey(self.rel.to, related_name=related_name),
            SORT_VALUE_FIELD_NAME:
                models.IntegerField(default=default_sort_value),
        }

        class Meta:
            db_table = '%s_%s_%s' % (
                cls._meta.app_label.lower(),
                cls._meta.object_name.lower(),
                field_name.lower())
            app_label = cls._meta.app_label
            ordering = (SORT_VALUE_FIELD_NAME,)

        attrs = {
            '__module__': module,
            'Meta': Meta,
            '_sort_field_name': SORT_VALUE_FIELD_NAME,
            '__unicode__': lambda s: 'pk=%d' % s.pk,
        }

        # Add in any fields that were provided
        if fields:
            attrs.update(fields)

        # Create the class, which automatically triggers ModelBase processing
        model = type(model_name, (models.Model,), attrs)
        model.related_name = related_name

        return model

    def contribute_to_class(self, cls, name):
        if self.sorted:
            # apply some meta data to the field to have it available in
            # different places, like ReverseSortedManyRelatedObjectsDescriptor
            self.from_model = cls
            self.field_name = name
            model = self.create_intermediary_model(cls, name)
            self.rel.through = model
            setattr(cls, '_%s_through' % name, self.rel.through)
            super(SortedManyToManyField, self).contribute_to_class(cls, name)
            setattr(cls, self.name, ReverseSortedManyRelatedObjectsDescriptor(self))
        else:
            super(SortedManyToManyField, self).contribute_to_class(cls, name)

    def formfield(self, **kwargs):
        defaults = {}
        if self.sorted:
            defaults['form_class'] = SortedMultipleChoiceField
        defaults.update(kwargs)
        return super(SortedManyToManyField, self).formfield(**defaults)
