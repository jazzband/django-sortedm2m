# -*- coding: utf-8 -*-
import os
import shutil

from django.core.management import call_command
from django.db.utils import OperationalError, ProgrammingError
from django.test import TransactionTestCase
from sortedm2m.compat import get_apps_from_state, get_field, get_rel
from sortedm2m_tests.migrations_tests.models import Gallery, Photo

from .compat import m2m_set
from .utils import capture_stdout


class TestMigrateCommand(TransactionTestCase):
    def test_migrate(self):
        with capture_stdout():
            call_command('migrate', interactive=False)


class TestMigrations(TransactionTestCase):
    def tearDown(self):
        # Remove created migrations.
        migrations_path = os.path.join(
            os.path.dirname(__file__),
            'migrations_tests',
            'django17_migrations')
        if os.path.exists(migrations_path):
            for filename in os.listdir(migrations_path):
                if filename not in ('__init__.py', '0001_initial.py'):
                    filepath = os.path.join(migrations_path, filename)
                    if os.path.isdir(filepath):
                        shutil.rmtree(filepath)
                    else:
                        os.remove(filepath)

    def test_defined_migration(self):
        photo = Photo.objects.create(name='Photo')
        gallery = Gallery.objects.create(name='Gallery')
        # photos field is already migrated.
        self.assertEqual(gallery.photos.count(), 0)
        # photos2 field is not yet migrated.
        self.assertRaises((OperationalError, ProgrammingError), gallery.photos2.count)

    def test_make_migration(self):
        with capture_stdout():
            call_command('makemigrations', 'migrations_tests')
            call_command('migrate')

        gallery = Gallery.objects.create(name='Gallery')
        self.assertEqual(gallery.photos.count(), 0)
        self.assertEqual(gallery.photos2.count(), 0)

    def test_stable_sorting_after_migration(self):
        with capture_stdout():
            call_command('makemigrations', 'migrations_tests')
            call_command('migrate')

        p1 = Photo.objects.create(name='A')
        p2 = Photo.objects.create(name='C')
        p3 = Photo.objects.create(name='B')

        gallery = Gallery.objects.create(name='Gallery')
        m2m_set(gallery, "photos", [p1, p2, p3])
        m2m_set(gallery, "photos2", [p3, p1, p2])

        gallery = Gallery.objects.get(name='Gallery')

        self.assertEqual(list(gallery.photos.values_list('name', flat=True)), ['A', 'C', 'B'])
        self.assertEqual(list(gallery.photos2.values_list('name', flat=True)), ['B', 'A', 'C'])

        m2m_set(gallery, "photos", [p3, p2])
        self.assertEqual(list(gallery.photos.values_list('name', flat=True)), ['B', 'C'])

        gallery = Gallery.objects.get(name='Gallery')
        self.assertEqual(list(gallery.photos.values_list('name', flat=True)), ['B', 'C'])


class TestAlterSortedManyToManyFieldOperation(TransactionTestCase):
    def setUp(self):
        from django.db.migrations.executor import MigrationExecutor
        from django.db.migrations.loader import MigrationLoader
        from django.db import connection

        self.migration_executor = MigrationExecutor(connection)
        self.migration_loader = MigrationLoader(connection)
        self.state_0001 = self.migration_loader.project_state(
            ('altersortedmanytomanyfield_tests', '0001_initial'))
        self.state_0002 = self.migration_loader.project_state(
            ('altersortedmanytomanyfield_tests', '0002_alter_m2m_fields'))
        self.state_0001_apps = get_apps_from_state(self.state_0001)
        self.state_0002_apps = get_apps_from_state(self.state_0002)

        # Make sure we are at the latest migration when starting the test.
        with capture_stdout():
            call_command('migrate', 'altersortedmanytomanyfield_tests')

    def test_apply_migrations_backwards(self):
        with capture_stdout():
            call_command('migrate', 'altersortedmanytomanyfield_tests', '0001')

    def test_operation_m2m_to_sorted_m2m(self):

        # Let's start with state after 0001
        with capture_stdout():
            call_command('migrate', 'altersortedmanytomanyfield_tests', '0001')

        Target = self.state_0001_apps.get_model(
            'altersortedmanytomanyfield_tests', 'target')
        M2MToSortedM2M = self.state_0001_apps.get_model(
            'altersortedmanytomanyfield_tests', 'm2mtosortedm2m')

        t1 = Target.objects.create(pk=1)
        t2 = Target.objects.create(pk=2)
        t3 = Target.objects.create(pk=3)

        field = get_field(M2MToSortedM2M,'m2m')
        through_model = get_rel(field).through
        # No ordering is in place.
        self.assertTrue(not through_model._meta.ordering)


        instance = M2MToSortedM2M.objects.create(pk=1)
        instance.m2m.add(t3)
        instance.m2m.add(t1)
        instance.m2m.add(t2)

        # We cannot assume any particular order now.

        # Migrate to state 0002, then we should be able to apply order.
        with capture_stdout():
            call_command('migrate', 'altersortedmanytomanyfield_tests', '0002')

        Target = self.state_0002_apps.get_model(
            'altersortedmanytomanyfield_tests', 'target')
        M2MToSortedM2M = self.state_0002_apps.get_model(
            'altersortedmanytomanyfield_tests', 'm2mtosortedm2m')

        t1 = Target.objects.get(pk=1)
        t2 = Target.objects.get(pk=2)
        t3 = Target.objects.get(pk=3)

        field = get_field(M2MToSortedM2M,'m2m')
        through_model = get_rel(field).through
        # Now, ordering is there.
        self.assertTrue(list(through_model._meta.ordering), ['sort_value'])

        instance = M2MToSortedM2M.objects.get(pk=1)
        self.assertEqual(list(instance.m2m.order_by('pk')), [t1, t2, t3])

        m2m_set(instance, "m2m", [t3, t1, t2])

        self.assertEqual(list(instance.m2m.all()), [t3, t1, t2])

        instance.m2m.remove(t1)
        instance.m2m.remove(t2)
        instance.m2m.add(t2)
        instance.m2m.add(t1)

        self.assertEqual(list(instance.m2m.all()), [t3, t2, t1])
