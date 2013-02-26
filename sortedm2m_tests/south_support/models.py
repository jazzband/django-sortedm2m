# -*- coding: utf-8 -*-
from django.db import models
from sortedm2m.fields import SortedManyToManyField


class Photo(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name


class Gallery(models.Model):
    name = models.CharField(max_length=30)
    photos = SortedManyToManyField(Photo)

    def __unicode__(self):
        return self.name


class UnsortedGallery(models.Model):
    name = models.CharField(max_length=30)
    photos = SortedManyToManyField(Photo, sorted=False)

    def __unicode__(self):
        return self.name
