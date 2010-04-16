# -*- coding: utf-8 -*-
from django import forms
from django.db import models
from django.test import TestCase
from sortedm2m.fields import SortedManyToManyField
from sortedm2m.forms import SortedMultipleChoiceField


class Book(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Shelf(models.Model):
    books = SortedManyToManyField(Book, related_name='shelves')


class Store(models.Model):
    books = SortedManyToManyField('sortedm2m.Book', related_name='stores')


class MessyStore(models.Model):
    books = SortedManyToManyField('Book',
        sorted=False,
        related_name='messy_stores')


class TestSortedManyToManyField(TestCase):
    model = Shelf

    def setUp(self):
        self.books = [Book.objects.create(name=c) for c in 'abcdefghik']

    def test_adding_items(self):
        shelf = self.model.objects.create()
        self.assertEqual(list(shelf.books.all()), [])

        shelf.books.add(self.books[2])
        self.assertEqual(list(shelf.books.all()), [self.books[2]])

        shelf.books.add(self.books[5], self.books[1])
        self.assertEqual(list(shelf.books.all()), [
            self.books[2],
            self.books[5],
            self.books[1]])

        # adding the same item again will append it another time
        shelf.books.add(self.books[2])
        self.assertEqual(list(shelf.books.all()), [
            self.books[2],
            self.books[5],
            self.books[1],
            self.books[2]])

    def test_set_items(self):
        shelf = self.model.objects.create()
        self.assertEqual(list(shelf.books.all()), [])

        shelf.books = self.books[5:2:-1]
        self.assertEqual(list(shelf.books.all()), [
            self.books[5],
            self.books[4],
            self.books[3]])

        shelf.books = [self.books[9]]
        self.assertEqual(list(shelf.books.all()), [
            self.books[9]])

        shelf.books = []
        self.assertEqual(list(shelf.books.all()), [])

    def test_remove_items(self):
        shelf = self.model.objects.create()
        shelf.books = self.books[2:5]
        self.assertEqual(list(shelf.books.all()), [
            self.books[2],
            self.books[3],
            self.books[4]])

        shelf.books.remove(self.books[3])
        self.assertEqual(list(shelf.books.all()), [
            self.books[2],
            self.books[4]])

        shelf.books.remove(self.books[2], self.books[4])
        self.assertEqual(list(shelf.books.all()), [])

#    def test_add_relation_by_hand(self):
#        shelf = self.model.objects.create()
#        shelf.books = self.books[2:5]
#        self.assertEqual(list(shelf.books.all()), [
#            self.books[2],
#            self.books[3],
#            self.books[4]])
#
#        shelf.books.create()
#        self.assertEqual(list(shelf.books.all()), [
#            self.books[2],
#            self.books[3],
#            self.books[4]])


class TestStringReference(TestSortedManyToManyField):
    '''
    Test the same things as ``TestSortedManyToManyField`` but using a model
    that using a string to reference the relation where the m2m field should
    point to.
    '''
    model = Store


class SortedForm(forms.Form):
    values = SortedMultipleChoiceField(
        queryset=Book.objects.all(),
        required=False)

class TestSortedFormField(TestCase):
    def setUp(self):
        self.books = [Book.objects.create(name=c) for c in 'abcdefghik']

    def test_empty_field(self):
        form = SortedForm({'values': []})
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data['values'])

    def test_sorted_field_input(self):
        form = SortedForm({'values': [4,2,9]})
        self.assertTrue(form.is_valid())
        self.assertEqual(list(form.cleaned_data['values']), [
                self.books[3],
                self.books[1],
                self.books[8]])

        form = SortedForm({'values': [book.pk for book in self.books[::-1]]})
        self.assertTrue(form.is_valid())
        self.assertEqual(list(form.cleaned_data['values']), self.books[::-1])

    def test_form_field_on_model_field(self):
        class ShelfForm(forms.ModelForm):
            class Meta:
                model = Shelf

        form = ShelfForm()
        self.assertTrue(
            isinstance(form.fields['books'], SortedMultipleChoiceField))

        class MessyStoreForm(forms.ModelForm):
            class Meta:
                model = MessyStore

        form = MessyStoreForm()
        self.assertFalse(
            isinstance(form.fields['books'], SortedMultipleChoiceField))
        self.assertTrue(
            isinstance(form.fields['books'], forms.ModelMultipleChoiceField))
