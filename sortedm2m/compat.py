
from django.db import models


def get_model_name(model):
    return model._meta.model_name


def get_foreignkey_field_kwargs(field):
    return {
        'db_tablespace': field.db_tablespace,
        'db_constraint': get_rel(field).db_constraint,
        'on_delete': models.CASCADE,
    }


def get_field(model, field_name):
    return model._meta.get_field(field_name)


def get_apps_from_state(migration_state):
    return migration_state.apps


def allow_migrate_model(self, connection_alias, model):
    return self.allow_migrate_model(connection_alias, model)


def get_rel(f):
    return f.remote_field


def get_rel_to(f):
    return f.remote_field.model
