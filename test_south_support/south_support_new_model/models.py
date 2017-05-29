# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from ..models import Photo
from sortedm2m.fields import SortedManyToManyField


# this model is not considered in the existing migrations. South will try to
# create this model.
@python_2_unicode_compatible
class CompleteNewPhotoStream(models.Model):
    name = models.CharField(max_length=30)
    new_photos = SortedManyToManyField(Photo, sorted=True)

    def __str__(self):
        return self.name
