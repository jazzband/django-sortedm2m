# -*- coding: utf-8 -*-
import sys
from django.db import router
from django.db.models import signals,Model
from django.db.models.fields.related import add_lazy_relation, create_many_related_manager
from django.db.models.fields.related import ManyToManyField, ReverseManyRelatedObjectsDescriptor,ManyRelatedObjectsDescriptor
from django.db.models.fields.related import RECURSIVE_RELATIONSHIP_CONSTANT
from django.conf import settings
from django.utils.functional import curry,cached_property
from sortedm2m.forms import SortedMultipleChoiceField


if sys.version_info[0] < 3:
    string_types = basestring
else:
    string_types = str


SORT_VALUE_FIELD_NAME = 'sort_value'
REV_SORT_VALUE_FIELD_NAME = 'rev_sort_value'


def create_sorted_many_to_many_intermediate_model(field, klass):
    from django.db import models
    managed = True
    if isinstance(field.rel.to, string_types) and field.rel.to != RECURSIVE_RELATIONSHIP_CONSTANT:
        to_model = field.rel.to
        to = to_model.split('.')[-1]

        def set_managed(field, model, cls):
            field.rel.through._meta.managed = model._meta.managed or cls._meta.managed
        add_lazy_relation(klass, field, to_model, set_managed)
    elif isinstance(field.rel.to, string_types):
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
        from_ = klass._meta.object_name.lower()
        to = to.lower()
    meta = type(str('Meta'), (object,), {
        'db_table': field._get_m2m_db_table(klass._meta),
        'managed': managed,
        'auto_created': klass,
        'app_label': klass._meta.app_label,
        'unique_together': (from_, to),
        'ordering': (field.sort_value_field_name,),
        'verbose_name': '%(from)s-%(to)s relationship' % {'from': from_, 'to': to},
        'verbose_name_plural': '%(from)s-%(to)s relationships' % {'from': from_, 'to': to},
    })
    # Construct and return the new class.

    return type(str(name), (models.Model,), {
        'Meta': meta,
        '__module__': klass.__module__,
        from_: models.ForeignKey(klass, related_name='%s+' % name),
        to: models.ForeignKey(to_model, related_name='%s+' % name),
        field.sort_value_field_name: models.IntegerField(),
        field.rev_sort_value_field_name: models.IntegerField(),
        '_sort_field_name': field.sort_value_field_name,
        '_rev_sort_field_name': field.rev_sort_value_field_name,
        '_from_field_name': from_,
        '_to_field_name': to,
    })


def create_sorted_many_related_manager(superclass, rel,rev=False):
    RelatedManager = create_many_related_manager(superclass, rel)

    class SortedRelatedManager(RelatedManager):
        def get_query_set(self):
            # We use ``extra`` method here because we have no other access to
            # the extra sorting field of the intermediary model. The fields
            # are hidden for joins because we set ``auto_created`` on the
            # intermediary's meta options.
            return super(SortedRelatedManager, self).\
                get_query_set().\
                extra(order_by=['%s.%s' % (
                    rel.through._meta.db_table,
                    rel.through._sort_field_name if not rev else rel.through._rev_sort_field_name,
                )])

        if not hasattr(RelatedManager, '_get_fk_val'):
            @property
            def _fk_val(self):
                return self._pk_val

        def _add_items(self, source_field_name, target_field_name, *objs):
            # source_field_name: the PK fieldname in join_table for the source object
            # target_field_name: the PK fieldname in join_table for the target object
            # *objs - objects to add. Either object instances, or primary keys of object instances.
            # If there aren't any objects, there is nothing to do.
            if objs:
                new_ids = []
                for obj in objs:
                    if isinstance(obj, self.model):
                        if not router.allow_relation(obj, self.instance):
                            raise ValueError('Cannot add "%r": instance is on database "%s", value is on database "%s"' %
                                (obj, self.instance._state.db, obj._state.db))
                        if hasattr(self, '_get_fk_val'):  # Django>=1.5
                            fk_val = self._get_fk_val(obj, target_field_name)
                            if fk_val is None:
                                raise ValueError('Cannot add "%r": the value for field "%s" is None' %
                                                 (obj, target_field_name))
                            new_ids.append(self._get_fk_val(obj, target_field_name))
                        else:  # Django<1.5
                            new_ids.append(obj.pk)
                    elif isinstance(obj, Model):
                        raise TypeError("'%s' instance expected, got %r" % (self.model._meta.object_name, obj))
                    else:
                        new_ids.append(obj)
                db = router.db_for_write(self.through, instance=self.instance)
                vals = self.through._default_manager.using(db).values_list(target_field_name, flat=True)
                vals = vals.filter(**{
                    source_field_name: self._fk_val,
                    '%s__in' % target_field_name: new_ids,
                })
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
                rev_sort_field_name = self.through._rev_sort_field_name
                #sort_field = self.through._meta.get_field_by_name(sort_field_name)[0]
                for obj_id in new_ids:
                    self.through._default_manager.using(db).create(**{
                        '%s_id' % source_field_name: self._fk_val,  # Django 1.5 compatibility
                        '%s_id' % target_field_name: obj_id,
                        sort_field_name: self.get_sort_order_value(self._fk_val,obj_id,rev),
                        rev_sort_field_name: self.get_sort_order_value(self._fk_val,obj_id, not rev),
                    })
                if self.reverse or source_field_name == self.source_field_name:
                    # Don't send the signal when we are inserting the
                    # duplicate data row for symmetrical reverse entries.
                    signals.m2m_changed.send(sender=rel.through, action='post_add',
                        instance=self.instance, reverse=self.reverse,
                        model=self.model, pk_set=new_ids_set, using=db)

        def get_sort_order_value(self,fk,pk,is_rev):
            from django.db.models import Max
            model=self.through
            return (model.objects.filter(**{
                '%s_id' % self.source_field_name if not is_rev else self.target_field_name:fk if not is_rev else pk
            }).aggregate(max_order=Max(self.through._sort_field_name if rev == is_rev else self.through._rev_sort_field_name))["max_order"] or 0)+1

        def insert(self,objOrObjs,index):
            """ Function doc

            @param PARAM: objOrObjs=要插入的元素或元素列表或元素Queryset,index=插入的位置
            @return RETURN:
            """
            from django.db.models.query import QuerySet
            if isinstance(objOrObjs,QuerySet):
                objs=list(objOrObjs)
            elif isinstance(objOrObjs,list):
                objs=objOrObjs
            elif isinstance(objOrObjs,self.model):
                objs=[objOrObjs]
            else:
                raise TypeError("'%s' instance expected, got %r" % (self.model._meta.object_name, objOrObjs))

            length=len(objs)
            model=self.through
            queryset=model.objects.filter(**{
                self.source_field_name+"_id":self._fk_val
            })
            count=queryset.count()
            assert index<=count and index>=0,"index must between 0 to query count"
            if index==count:
                return self.add(*objs)
            else:
                trailItem=list(queryset[index:])
                model.objects.filter(pk__in=[item.pk for item in trailItem]).delete()
                self.add(*objs)
                sort_field=model._sort_field_name if not rev else model._rev_sort_field_name
                for item in trailItem:
                    item.__setattr__(
                        sort_field,item.__getattribute__(sort_field)+length
                    )

                model.objects.bulk_create(trailItem)

        def move(self,obj,vector):
            """move element order,vector can be integer,+1 is move one postion forward,-1 is move one position backward"""
            model=self.through
                #bridge=model.get(**{
                    #self.source_field_name+"_id":self._fk_val,
                    #self.target_field_name+"_id":obj.pk
                #})
            all_bridges=model.objects.filter(**{
                self.source_field_name+"_id":self._fk_val
            })
            all_bridges_list=list(all_bridges)
            finded=False
            for obj_index,bridge in enumerate(all_bridges_list):
                if bridge.__getattribute__(self.target_field_name+"_id")==obj.pk:
                    finded=True
                    break
            assert finded,"obj not add in item"
            #obj_index=all_bridges_list.index(bridge)
            target_index=obj_index+vector
            assert 0<=target_index<len(all_bridges_list),"move index must between items"
            start=min(obj_index,target_index)
            end=max(obj_index,target_index)
            if vector>0:
                start+=1
                offset=-1
                new_bridge_index=end
            elif vector<0:
                end-=1
                offset=1
                new_bridge_index=start
            else:
                return
            middle_bridge=all_bridges_list[start:end+1]
            sort_field=model._sort_field_name if not rev else model._rev_sort_field_name
            model.objects.filter(pk__in=[item.pk for item in middle_bridge]+[bridge.pk]).delete()
            bridge.__setattr__(
                sort_field,
                all_bridges_list[new_bridge_index].__getattribute__(sort_field)
            )
            for item in middle_bridge:
                item.__setattr__(
                    sort_field,item.__getattribute__(sort_field)+offset
                )
            model.objects.bulk_create(middle_bridge+[bridge])
            return

    return SortedRelatedManager


class ReverseSortedManyRelatedObjectsDescriptor(ReverseManyRelatedObjectsDescriptor):
    @property
    def related_manager_cls(self):
        return create_sorted_many_related_manager(
            self.field.rel.to._default_manager.__class__,
            self.field.rel
        )


class SortedManyRelatedObjectsDescriptor(ManyRelatedObjectsDescriptor):
    @cached_property
    def related_manager_cls(self):
        # Dynamically create a class that subclasses the related
        # model's default manager.
        return create_sorted_many_related_manager(
            self.related.model._default_manager.__class__,
            self.related.field.rel,
            rev=True
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
        self.rev_sort_value_field_name = kwargs.pop(
            'rev_sort_value_field_name',
            REV_SORT_VALUE_FIELD_NAME)
        super(SortedManyToManyField, self).__init__(to, **kwargs)
        if self.sorted:
            self.help_text = kwargs.get('help_text', None)

    def contribute_to_related_class(self, cls, related):
        super(SortedManyToManyField,self).contribute_to_related_class(cls,related)
        if not self.rel.is_hidden() and not related.model._meta.swapped:
            setattr(cls, related.get_accessor_name(), SortedManyRelatedObjectsDescriptor(related))

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
        if isinstance(self.rel.through, string_types):
            def resolve_through_model(field, model, cls):
                field.rel.through = model
            add_lazy_relation(cls, self, self.rel.through, resolve_through_model)

        if hasattr(cls._meta, 'duplicate_targets'):  # Django<1.5
            if isinstance(self.rel.to, string_types):
                target = self.rel.to
            else:
                target = self.rel.to._meta.db_table
            cls._meta.duplicate_targets[self.column] = (target, "m2m")

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
            (%(sort_field)r, models.IntegerField()),
            (%(rev_sort_field)r, models.IntegerField())
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
                    "rev_sort_field": self.field.rev_sort_value_field_name,
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
