# -*- coding: utf-8 -*-
import os
import sys
from StringIO import StringIO

from django.db import connection
from django.db.models.fields import FieldDoesNotExist
from django.db.utils import OperationalError
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import six

from sortedm2m_tests.migrations_tests.models import Gallery, Photo


str_ = six.text_type


class TestMigrateCommand(TestCase):
    def setUp(self):
        sys.stdout = StringIO()
        self.orig_stdout = sys.stdout

    def tearDown(self):
        sys.stdout = self.orig_stdout

    def test_migrate(self):
        call_command('migrate', interactive=False)


class TestMigrations(TestCase):
    def setUp(self):
        sys.stdout = StringIO()
        self.orig_stdout = sys.stdout

    def tearDown(self):
        sys.stdout = self.orig_stdout

        # Remove created migrations.
        migrations_path = os.path.join(
            os.path.dirname(__file__),
            'migrations_tests',
            'migrations')
        for filename in os.listdir(migrations_path):
            if filename not in ('__init__.py', '0001_initial.py'):
                os.remove(os.path.join(migrations_path, filename))

    def test_defined_migration(self):
        photo = Photo.objects.create(name='Photo')
        gallery = Gallery.objects.create(name='Gallery')
        # photos field is already migrated
        self.assertEqual(gallery.photos.count(), 0)
        # photos2 field is not yet migrated
        self.assertRaises(OperationalError, gallery.photos2.count)

    def test_make_migration(self):
        call_command('makemigrations', 'migrations_tests')
        call_command('migrate')

        gallery = Gallery.objects.create(name='Gallery')
        self.assertEqual(gallery.photos.count(), 0)
        self.assertEqual(gallery.photos2.count(), 0)

    def test_stable_sorting_after_migration(self):
        call_command('makemigrations', 'migrations_tests')
        call_command('migrate')

        p1 = Photo.objects.create(name='A')
        p2 = Photo.objects.create(name='C')
        p3 = Photo.objects.create(name='B')

        gallery = Gallery.objects.create(name='Gallery')
        gallery.photos = [p1, p2, p3]
        gallery.photos2 = [p3, p1, p2]

        gallery = Gallery.objects.get(name='Gallery')

        self.assertEqual(list(gallery.photos.values_list('name', flat=True)), ['A', 'C', 'B'])
        self.assertEqual(list(gallery.photos2.values_list('name', flat=True)), ['B', 'A', 'C'])

        gallery.photos = [p3, p2]
        self.assertEqual(list(gallery.photos.values_list('name', flat=True)), ['B', 'C'])

        gallery = Gallery.objects.get(name='Gallery')
        self.assertEqual(list(gallery.photos.values_list('name', flat=True)), ['B', 'C'])
