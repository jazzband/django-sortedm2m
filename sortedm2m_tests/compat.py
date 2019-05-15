import django
import six


StringIO = six.StringIO


def m2m_set(instance, field_name, objs):
    if django.VERSION > (1, 9):
        getattr(instance, field_name).set(objs)
    else:
        setattr(instance, field_name, objs)