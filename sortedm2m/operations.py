from django.db import models
from django.db.migrations.operations import AlterField

from sortedm2m.fields import SORT_VALUE_FIELD_NAME
from .compat import get_field
from .compat import get_apps_from_state
from .compat import allow_migrate_model


class AlterSortedManyToManyField(AlterField):
    """A migration operation to transform a ManyToManyField into a
    SortedManyToManyField and vice versa."""

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        to_apps = get_apps_from_state(to_state)
        to_model = to_apps.get_model(app_label, self.model_name)
        if allow_migrate_model(self, schema_editor.connection.alias, to_model):
            to_field = get_field(to_model, self.name)

            from_apps = get_apps_from_state(from_state)
            from_model = from_apps.get_model(app_label, self.model_name)
            from_field = get_field(from_model, self.name)

            to_m2m_model = to_field.rel.through
            from_m2m_model = from_field.rel.through

            # M2M -> SortedM2M
            if getattr(to_field, 'sorted', False):
                self.add_sort_value_field(schema_editor, to_m2m_model)
            # SortedM2M -> M2M
            elif getattr(from_field, 'sorted', False):
                self.remove_sort_value_field(schema_editor, from_m2m_model)
            else:
                raise TypeError(
                    '{operation} should only be used when changing a '
                    'SortedManyToManyField into a ManyToManyField or a '
                    'ManyToManyField into a SortedManyToManyField.'
                    .format(operation=self.__class__.__name__))

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        from_apps = get_apps_from_state(from_state)
        from_model = from_apps.get_model(app_label, self.model_name)
        from_field = get_field(from_model, self.name)

        to_apps = get_apps_from_state(to_state)
        to_model = to_apps.get_model(app_label, self.model_name)

        if allow_migrate_model(self, schema_editor.connection.alias, to_model):
            to_field = get_field(to_model, self.name)
            from_m2m_model = from_field.rel.through
            to_m2m_model = to_field.rel.through

            # The `to_state` is the OLDER state.

            # M2M -> SortedM2M (backwards)
            if getattr(to_field, 'sorted', False):
                self.add_sort_value_field(schema_editor, to_m2m_model)
            # SortedM2M -> M2M (backwards)
            elif getattr(from_field, 'sorted', False):
                self.remove_sort_value_field(schema_editor, from_m2m_model)
            else:
                raise TypeError(
                    '{operation} should only be used when changing a '
                    'SortedManyToManyField into a ManyToManyField or a '
                    'ManyToManyField into a SortedManyToManyField.'
                    .format(operation=self.__class__.__name__))

    def add_sort_value_field(self, schema_editor, model):
        field = self.make_sort_by_field(model)
        schema_editor.add_field(model, field)

    def remove_sort_value_field(self, schema_editor, model):
        field = get_field(model, SORT_VALUE_FIELD_NAME)
        schema_editor.remove_field(model, field)

    def make_sort_by_field(self, model):
        field = models.IntegerField(name=SORT_VALUE_FIELD_NAME, default=0)
        field.set_attributes_from_name(SORT_VALUE_FIELD_NAME)
        return field
