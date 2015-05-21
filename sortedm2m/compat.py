import django

try:
    from django.apps import apps
except ImportError:
    apps = None


if apps is not None:
    get_model = apps.get_model
else:
    from django.db.models import get_model


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
