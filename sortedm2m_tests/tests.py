import django

# Make tests compatible with Django 1.5 and lower.
if django.VERSION < (1, 6):
    from .test_forms import *
    from .test_field import *
    from .test_migrations import *
