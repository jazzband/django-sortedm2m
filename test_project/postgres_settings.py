from .settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'sortedm2m',
        'USER': 'sortedm2m',
        'PASSWORD': 'sortedm2m',
    },
}
