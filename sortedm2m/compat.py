import django

try:
    from django.apps import apps
except ImportError:
    apps = None


if apps is not None:
    get_model = apps.get_model
else:
    from django.db.models import get_model


try:
    from django.db.models.fields.related_descriptors import create_forward_many_to_many_manager
except ImportError:
    # Django <= 1.8 support.
    from django.db.models.fields.related import create_many_related_manager as create_forward_many_to_many_manager


def get_model_name(model):
    # Django 1.5 support.
    if not hasattr(model._meta, 'model_name'):
        return model._meta.object_name.lower()
    else:
        return model._meta.model_name


def get_foreignkey_field_kwargs(field):
    # Django 1.5 support.
    if django.VERSION < (1, 6):
        return {}
    else:
        return dict(
            db_tablespace=field.db_tablespace,
            db_constraint=field.rel.db_constraint)


def get_field(model, field_name):
    if django.VERSION < (1, 8):
        return model._meta.get_field_by_name(field_name)[0]
    else:
        return model._meta.get_field(field_name)


def get_apps_from_state(migration_state):
    if django.VERSION < (1, 8):
        return migration_state.render()
    else:
        return migration_state.apps


def allow_migrate_model(self, connection_alias, model):
    if django.VERSION < (1, 8):
        return self.allowed_to_migrate(connection_alias, model)
    else:
        return self.allow_migrate_model(connection_alias, model)
