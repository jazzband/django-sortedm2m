# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from sortedm2m.fields import SortedManyToManyField


@python_2_unicode_compatible
class Photo(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Gallery(models.Model):
    name = models.CharField(max_length=30)
    photos = SortedManyToManyField(Photo)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class UnsortedGallery(models.Model):
    name = models.CharField(max_length=30)
    photos = SortedManyToManyField(Photo, sorted=False)

    def __str__(self):
        return self.name
