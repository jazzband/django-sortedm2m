# -*- coding: utf-8 -*-
from django.db import models
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from sortedm2m.fields import SortedManyToManyField


@python_2_unicode_compatible
class Car(models.Model):
    plate = models.CharField(max_length=50)

    def __str__(self):
        return self.plate


@python_2_unicode_compatible
class BaseCarThrough(object):
    def __str__(self):
        return str(self.car) + " in " + str(self.parkingarea)


@python_2_unicode_compatible
class ParkingArea(models.Model):
    name = models.CharField(max_length=50)
    cars = SortedManyToManyField(Car, base_class=BaseCarThrough)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('parkingarea', (self.pk,))
