# -*- coding: utf-8 -*-
from django.db import models
from sortedm2m.fields import SortedManyToManyField


class Shelf(models.Model):
    books = SortedManyToManyField('Book', related_name='shelves')


class Book(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class DoItYourselfShelf(models.Model):
    books = SortedManyToManyField(Book,
        sort_value_field_name='diy_sort_number',
        related_name='diy_shelves')


class Store(models.Model):
    books = SortedManyToManyField('sortedm2m_tests.Book', related_name='stores')


class MessyStore(models.Model):
    books = SortedManyToManyField('Book',
        sorted=False,
        related_name='messy_stores')


class SelfReference(models.Model):
    me = SortedManyToManyField('self', related_name='hide+')

    def __unicode__(self):
        return unicode(self.pk)
