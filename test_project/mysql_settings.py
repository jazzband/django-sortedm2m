from .settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'localhost',
        'NAME': 'sortedm2m',
        'USER': 'sortedm2m',
        'PASSWORD': 'sortedm2m',
    },
}
