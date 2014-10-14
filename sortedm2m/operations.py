from __future__ import unicode_literals

import django

from django.db import models
from django.db.migrations.operations import AlterField
from django.db.models.fields import NOT_PROVIDED
from django.utils import six
from django.utils.functional import curry

from sortedm2m.fields import SORT_VALUE_FIELD_NAME

class AlterSortedManyToManyField(AlterField):
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        super(AlterSortedManyToManyField, self).database_forwards(app_label, schema_editor, from_state, to_state)

        to = to_state.render().get_model(app_label, self.model_name)
        tf = to._meta.get_field_by_name(self.name)[0]
        m2m_model = tf.rel.through

        if hasattr(m2m_model._meta, 'db_table'):
            if hasattr(m2m_model, '_sort_field_name'):
                schema_editor.add_field(m2m_model, self.make_sort_by_field(m2m_model))

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        super(AlterSortedManyToManyField, self).database_backwards(app_label, schema_editor, from_state, to_state)

        f = from_state.render().get_model(app_label, self.model_name)
        ff = f._meta.get_field_by_name(self.name)[0]
        m2m_model = ff.rel.through

        if hasattr(m2m_model._meta, 'db_table'):
            if hasattr(m2m_model, '_sort_field_name'):
                schema_editor.remove_field(m2m_model, m2m_model._meta.get_field_by_name(SORT_VALUE_FIELD_NAME)[0])

    def make_sort_by_field(self, model):
        return models.IntegerField(name=SORT_VALUE_FIELD_NAME)

    def set_default_value(self, model):
        def default_sort_value(name):
            # Django 1.5 support.
            if django.VERSION < (1, 6):
                return model._default_manager.count()
            else:
                from django.db.utils import OperationalError
                try:
                    # We need to catch if the model is not yet migrated in the
                    # database. The default function is still called in this case while
                    # running the migration. So we mock the return value of 0.
                    return model._default_manager.count()
                except OperationalError:
                    return 0
        return curry(default_sort_value, model._meta.db_table)
