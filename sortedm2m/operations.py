from django.db import models
from django.db.migrations.operations import AlterField

from sortedm2m.fields import SORT_VALUE_FIELD_NAME


class AlterSortedManyToManyField(AlterField):
    """A migration operation to transform a ManyToManyField."""

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
