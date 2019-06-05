from django.db import models
from django.utils.translation import ugettext_lazy as _

from sortedm2m.fields import SortedManyToManyField


class Photo(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')

    def __str__(self):
        return self.name


class Gallery(models.Model):
    name = models.CharField(max_length=50)
    photos = SortedManyToManyField(Photo)
    photos2 = SortedManyToManyField(Photo, related_name='gallery2+')

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')

    def __str__(self):
        return self.name
