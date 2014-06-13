# -*- coding: utf-8 -*-
from django.db import models
from ..models import Photo
from sortedm2m.fields import SortedManyToManyField


# this model is not considered in the existing migrations. South will try to
# create this model.
class CompleteNewPhotoStream(models.Model):
    name = models.CharField(max_length=30)
    new_photos = SortedManyToManyField(Photo, sorted=True)

    def __unicode__(self):
        return self.name
