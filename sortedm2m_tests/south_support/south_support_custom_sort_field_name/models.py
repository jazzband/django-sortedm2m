# -*- coding: utf-8 -*-
from django.db import models
from ..models import Photo
from sortedm2m.fields import SortedManyToManyField


# this model is not considered in the existing migrations. South will try to
# create this model.
class FeaturedPhotos(models.Model):
    name = models.CharField(max_length=30)
    photos = SortedManyToManyField(Photo,
        sort_value_field_name='featured_nr')

    def __unicode__(self):
        return self.name
