# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from ..models import Photo
from sortedm2m.fields import SortedManyToManyField


# this model is already created in the schemamigrations but the ``photos``
# field is missing from the DB. So south will try to create it.
@python_2_unicode_compatible
class PhotoStream(models.Model):
    name = models.CharField(max_length=30)
    photos = SortedManyToManyField(Photo, sorted=True)

    def __str__(self):
        return self.name
