# -*- coding: utf-8 -*-
from __future__ import with_statement
import sys
import mock
from django.core.management import call_command
from django.test import TestCase

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

from .models import Gallery, Photo, UnsortedGallery


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
    def perform_migration(self, *args, **kwargs):
        stdout = StringIO()
        stderr = StringIO()
        with mock.patch('sys.stdout', stdout):
            with mock.patch('sys.stderr', stderr):
                call_command(*args, **kwargs)
        stdout.seek(0)
        stderr.seek(0)
        output = stdout.read()
        errput = stderr.read()
        return output, errput

    def assertExpectedStrings(self, expected_strings, output):
        last = 0
        for expect in expected_strings:
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

    def assertUnexpectedStrings(self, unexpected_strings, output):
        for unexpected in unexpected_strings:
            current = output.find(unexpected)
            if current != -1:
                self.fail(
                    "Following string is content of "
                    "south migration: %s" % unexpected)


    def test_new_model(self):
        from sortedm2m.fields import SORT_VALUE_FIELD_NAME

        output, errput = self.perform_migration(
            'schemamigration',
            'south_support_new_model',
            stdout=True,
            auto=True)

        self.assertExpectedStrings([
            "Adding SortedM2M table for field new_photos on 'CompleteNewPhotoStream'",
            "('%s', models.IntegerField())" % SORT_VALUE_FIELD_NAME,
        ], output)

        self.assertExpectedStrings([
            "+ Added model south_support_new_model.CompleteNewPhotoStream",
            "+ Added SortedM2M table for new_photos on south_support_new_model.CompleteNewPhotoStream",
        ], errput)

    def test_new_field(self):
        from sortedm2m.fields import SORT_VALUE_FIELD_NAME

        output, errput = self.perform_migration(
            'schemamigration',
            'south_support_new_field',
            stdout=True,
            auto=True)

        self.assertExpectedStrings([
            "Adding SortedM2M table for field photos on 'PhotoStream'",
            "('%s', models.IntegerField())" % SORT_VALUE_FIELD_NAME,
        ], output)

        self.assertExpectedStrings([
            "+ Added SortedM2M table for photos on south_support_new_field.PhotoStream",
        ], errput)
        self.assertUnexpectedStrings([
            "+ Added model south_support_new_field.PhotoStream",
        ], errput)

    def test_custom_sort_field_name(self):
        output, errput = self.perform_migration(
            'schemamigration',
            'south_support_custom_sort_field_name',
            stdout=True,
            auto=True)

        self.assertExpectedStrings([
            "Adding SortedM2M table for field photos on 'FeaturedPhotos'",
            "('featured_nr', models.IntegerField())",
        ], output)

        self.assertExpectedStrings([
            "+ Added model south_support_custom_sort_field_name.FeaturedPhotos",
            "+ Added SortedM2M table for photos on south_support_custom_sort_field_name.FeaturedPhotos",
        ], errput)
