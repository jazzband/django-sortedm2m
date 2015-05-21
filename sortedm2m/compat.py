try:
    from django.apps import apps
except ImportError:
    apps = None


if apps is None:
    get_model = apps.get_model
else:
    from django.db.models import get_model
