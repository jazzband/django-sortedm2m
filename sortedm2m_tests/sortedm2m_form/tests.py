# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.test import TestCase
from sortedm2m.forms import SortedMultipleChoiceField
from sortedm2m_tests.models import Book, Shelf, Store, MessyStore


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

    # regression test
    def test_form_field_with_only_one_value(self):
        form = SortedForm({'values': ''})
        self.assertEqual(len(form.errors), 0)
        form = SortedForm({'values': '1'})
        self.assertEqual(len(form.errors), 0)
        form = SortedForm({'values': '1,2'})
        self.assertEqual(len(form.errors), 0)
