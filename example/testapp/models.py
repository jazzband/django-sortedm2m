# -*- coding: utf-8 -*-
from django.db import models
from sortedm2m.fields import SortedManyToManyField


class Car(models.Model):
    plate = models.CharField(max_length=50)

    def __unicode__(self):
        return self.plate

class m2mprint:
    def __unicode__(self):
        return unicode(self.car) + " in " + unicode(self.parkingarea)

class ParkingArea(models.Model):
    name = models.CharField(max_length=50)
    cars = SortedManyToManyField(Car, base_class=m2mprint)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'parkingarea', (self.pk,), {}
