from django.db import models

from sortedm2m.fields import SortedManyToManyField

try:
    from django.urls import reverse  # pylint: disable=ungrouped-imports
except ImportError:
    from django.core.urlresolvers import reverse    # pylint: disable=ungrouped-imports


class Car(models.Model):
    plate = models.CharField(max_length=50)

    def __str__(self):
        return self.plate


class BaseCarThrough(object):
    def __str__(self):
        return str(self.car) + " in " + str(self.parkingarea)  # pylint: disable=no-member


class ParkingArea(models.Model):
    name = models.CharField(max_length=50)
    cars = SortedManyToManyField(Car, base_class=BaseCarThrough)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('parkingarea', (self.pk,))
