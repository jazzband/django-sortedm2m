# -*- coding: utf-8 -*-
from django import forms
from django.test import TestCase
from django.utils import six
from sortedm2m.forms import SortedMultipleChoiceField
from .models import Book, Shelf, Store, MessyStore


str_ = six.text_type


class SortedForm(forms.Form):
    values = SortedMultipleChoiceField(
        queryset=Book.objects.all(),
        required=False)


class TestSortedFormField(TestCase):
    def setUp(self):
        self.books = [Book.objects.create(name=c) for c in 'abcdefghik']
        (
            self.a, self.b, self.c, self.d, self.e, self.f, self.g, self.h,
            self.i, self.k) = self.books

    def test_empty_field(self):
        form = SortedForm({'values': []})
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data['values'])

    def test_sorted_field_input(self):
        form = SortedForm({'values': [self.d.pk, self.b.pk, self.i.pk]})
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
                fields = (
                    'books',
                )

        form = ShelfForm()
        self.assertTrue(
            isinstance(form.fields['books'], SortedMultipleChoiceField))

        class MessyStoreForm(forms.ModelForm):
            class Meta:
                model = MessyStore
                fields = (
                    'books',
                )

        form = MessyStoreForm()
        self.assertFalse(
            isinstance(form.fields['books'], SortedMultipleChoiceField))
        self.assertTrue(
            isinstance(form.fields['books'], forms.ModelMultipleChoiceField))

    # regression test
    def test_form_field_with_only_one_value(self):
        form = SortedForm({'values': ''})
        self.assertEqual(len(form.errors), 0)
        form = SortedForm({'values': str(self.a.pk)})
        self.assertEqual(len(form.errors), 0)
        form = SortedForm({'values': '{a.pk},{b.pk}'.format(a=self.a, b=self.b)})
        self.assertEqual(len(form.errors), 0)

    def test_for_attribute_in_label(self):
        form = SortedForm()
        rendered = str_(form['values'])
        self.assertTrue(' for="id_values_0"' in rendered)

        form = SortedForm(prefix='prefix')
        rendered = str_(form['values'])
        self.assertTrue(' for="id_prefix-values_0"' in rendered)

        # check that it will be escaped properly

        form = SortedForm(prefix='hacking"><a href="TRAP">')
        rendered = str_(form['values'])
        self.assertTrue(' for="id_hacking&quot;&gt;&lt;a href=&quot;TRAP&quot;&gt;-values_0"' in rendered)

    def test_input_id_is_escaped(self):
        form = SortedForm(prefix='hacking"><a href="TRAP">')
        rendered = str_(form['values'])
        self.assertTrue(' id="id_hacking&quot;&gt;&lt;a href=&quot;TRAP&quot;&gt;-values_0"' in rendered)

    def test_form_field_detects_reordering(self):
        form = SortedForm({'values': '{a.pk},{b.pk}'.format(a=self.a, b=self.b)})
        form.fields['values'].initial = [self.b.pk, self.a.pk]
        self.assertTrue('values' in form.changed_data)
