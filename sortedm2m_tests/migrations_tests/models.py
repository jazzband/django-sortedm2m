from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from sortedm2m.fields import SortedManyToManyField


@python_2_unicode_compatible
class Photo(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Gallery(models.Model):
    name = models.CharField(max_length=50)
    photos = SortedManyToManyField(Photo)
    photos2 = SortedManyToManyField(Photo, related_name='gallery2+')

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')

    def __str__(self):
        return self.name
