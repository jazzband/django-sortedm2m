# -*- coding: utf-8 -*-
from django.db import models
from sortedm2m.fields import SortedManyToManyField


class MessyStore(models.Model):
    books = SortedManyToManyField('Book',
        sorted=False,
        related_name='messy_stores')


class Book(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Shelf(models.Model):
    books = SortedManyToManyField(Book, related_name='shelves')


class Store(models.Model):
    books = SortedManyToManyField('sortedm2m_tests.Book', related_name='stores')
