# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from sortedm2m.fields import SortedManyToManyField


class BaseBookThrough(object):

    def __str__(self):
        return "Relationship to {0}".format(self.book.name)


class Shelf(models.Model):
    books = SortedManyToManyField('Book', related_name='shelves', base_class=BaseBookThrough)


@python_2_unicode_compatible
class Book(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class DoItYourselfShelf(models.Model):
    books = SortedManyToManyField(Book,
        sort_value_field_name='diy_sort_number',
        related_name='diy_shelves',
        base_class=BaseBookThrough)


class Store(models.Model):
    books = SortedManyToManyField('sortedm2m_tests.Book', related_name='stores')


class MessyStore(models.Model):
    books = SortedManyToManyField('Book',
        sorted=False,
        related_name='messy_stores')


@python_2_unicode_compatible
class SelfReference(models.Model):
    me = SortedManyToManyField('self', related_name='hide+')

    def __str__(self):
        return force_text(self.pk)
