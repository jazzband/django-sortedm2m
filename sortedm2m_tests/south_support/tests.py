from __future__ import with_statement
import mock
from django.core.management import call_command
from django.test import TestCase
from sortedm2m_tests.south_support.models import Gallery, Photo, \
    UnsortedGallery


class SouthMigratedModelTests(TestCase):
    def test_sorted_m2m(self):
        pic1 = Photo.objects.create(name='Picture 1')
        pic2 = Photo.objects.create(name='Picture 1')
        gallery = Gallery.objects.create(name='Gallery')
        gallery.photos.add(pic1)
        gallery.photos.add(pic2)
        self.assertEqual(list(gallery.photos.all()), [pic1, pic2])

    def test_unsorted_sorted_m2m(self):
        pic1 = Photo.objects.create(name='Picture 1')
        pic2 = Photo.objects.create(name='Picture 1')
        gallery = UnsortedGallery.objects.create(name='Gallery')
        gallery.photos.add(pic1)
        gallery.photos.add(pic2)
        self.assertEqual(set(gallery.photos.all()), set((pic1, pic2)))


class SouthSchemaMigrationTests(TestCase):
    def test_1(self):
        from StringIO import StringIO
        stdout = StringIO()
        stderr = StringIO()
        with mock.patch('sys.stdout', stdout):
            with mock.patch('sys.stderr', stderr):
                call_command('schemamigration', 'south_support', stdout=True, auto=True)
        stdout.seek(0)
        stderr.seek(0)
        output = stdout.read()
        errput = stderr.read()
        expected_out_strings = [
            "Adding SortedM2M table for field photos on 'PhotoStream'",
            "('sort_value', models.IntegerField())",
        ]
        last = 0

        for expect in expected_out_strings:
            current = output.find(expect)
            if current == -1:
                self.fail(
                    "Following string is missing from "
                    "south migration: %s" % expect)
            self.assertTrue(
                last < current,
                "Following string is not in correct position in "
                "south migration: %s" % expect)
            last = current

        expected_err_strings = [
            "+ Added model south_support.PhotoStream",
            "+ Added SortedM2M table for photos on south_support.PhotoStream",
        ]
        last = 0
        for expect in expected_err_strings:
            current = errput.find(expect)
            if current == -1:
                self.fail(
                    "Following string is missing from "
                    "south stderr: %s" % expect)
            self.assertTrue(
                last < current,
                "Following string is not in correct position in "
                "south stderr: %s" % expect)
            last = current
