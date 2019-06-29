from test_project.settings import *  # pylint: disable=unused-wildcard-import,wildcard-import

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'sortedm2m',
        "USER": os.environ.get('DJANGO_DB_USER', 'sortedm2m'),
        'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD', 'sortedm2m'),
    },
}
