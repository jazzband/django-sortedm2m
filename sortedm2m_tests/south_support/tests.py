from django.test import TestCase
from sortedm2m_tests.south_support.models import Gallery, Photo


class SouthTests(TestCase):
    def test_create(self):
        pic1 = Photo.objects.create(name='Picture 1')
        pic2 = Photo.objects.create(name='Picture 1')
        gallery = Gallery.objects.create(name='Gallery')
        gallery.photos.add(pic1)
        gallery.photos.add(pic2)
        self.assertEqual(list(gallery.photos.all()), [pic1, pic2])
