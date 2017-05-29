# Django settings for testsite project.
import os
import django


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'db.sqlite'),
    },
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'define in local settings file'

if django.VERSION >= (1, 10):
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
else:
    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    )

ROOT_URLCONF = 'example.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.staticfiles',

    'sortedm2m',
    'sortedm2m_tests',
    'sortedm2m_tests.migrations_tests',
    'sortedm2m_tests.altersortedmanytomanyfield_tests',

    'example.testapp',
)

MIGRATION_MODULES = {
    'migrations_tests': 'sortedm2m_tests.migrations_tests.django17_migrations',
    'altersortedmanytomanyfield_tests': 'sortedm2m_tests.altersortedmanytomanyfield_tests.django17_migrations',
}

import django

if django.VERSION >= (1, 6):
    TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Only test south for django versions lower as 1.7
# 1.7 introduced it's own migrations framework
if django.VERSION < (1, 7):
    INSTALLED_APPS = INSTALLED_APPS + (
        'south',
        'test_south_support',
        'test_south_support.south_support_new_model',
        'test_south_support.south_support_new_field',
        'test_south_support.south_support_custom_sort_field_name',
    )

if django.VERSION >= (1, 8):
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(PROJECT_ROOT, 'templates'),
            ],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]
else:
    TEMPLATE_DIRS = (
        os.path.join(PROJECT_ROOT, 'templates'),
    )
    TEMPLATE_DEBUG = DEBUG

try:
    from local_settings import *
except ImportError:
    pass
