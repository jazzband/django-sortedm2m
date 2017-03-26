# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from ..models import Photo
from sortedm2m.fields import SortedManyToManyField


# this model is not considered in the existing migrations. South will try to
# create this model.
@python_2_unicode_compatible
class FeaturedPhotos(models.Model):
    name = models.CharField(max_length=30)
    photos = SortedManyToManyField(Photo,
        sort_value_field_name='featured_nr')

    def __str__(self):
        return self.name
