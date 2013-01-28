# -*- coding: utf-8 -*-
from django.db.models.fields import FieldDoesNotExist
from django.test import TestCase
from sortedm2m_tests.models import Book, Shelf, DoItYourselfShelf, Store, \
    MessyStore, SelfReference


class TestSortedManyToManyField(TestCase):
    model = Shelf

    def setUp(self):
        self.books = [Book.objects.create(name=c) for c in 'abcdefghik']

    def test_adding_items(self):
        shelf = self.model.objects.create()
        self.assertEqual(list(shelf.books.all()), [])

        shelf.books.add(self.books[2])
        self.assertEqual(list(shelf.books.all()), [self.books[2]])

        # adding many with each in one call
        shelf.books.add(self.books[5])
        shelf.books.add(self.books[1])
        self.assertEqual(list(shelf.books.all()), [
            self.books[2],
            self.books[5],
            self.books[1]])

        # adding the same item again won't append another one, order remains
        # the same
        shelf.books.add(self.books[2])
        self.assertEqual(list(shelf.books.all()), [
            self.books[2],
            self.books[5],
            self.books[1]])

        shelf.books.clear()
        self.assertEqual(list(shelf.books.all()), [])

        # adding many with all in the same call
        shelf.books.add(self.books[3], self.books[1], self.books[2])
        self.assertEqual(list(shelf.books.all()), [
            self.books[3],
            self.books[1],
            self.books[2]])

    def test_adding_items_by_pk(self):
        shelf = self.model.objects.create()
        self.assertEqual(list(shelf.books.all()), [])

        shelf.books.add(self.books[2].pk)
        self.assertEqual(list(shelf.books.all()), [self.books[2]])

        shelf.books.add(self.books[5].pk, unicode(self.books[1].pk))
        self.assertEqual(list(shelf.books.all()), [
            self.books[2],
            self.books[5],
            self.books[1]])

        shelf.books.clear()
        self.assertEqual(list(shelf.books.all()), [])

        shelf.books.add(self.books[3].pk, self.books[1], unicode(self.books[2].pk))
        self.assertEqual(list(shelf.books.all()), [
            self.books[3],
            self.books[1],
            self.books[2]])

    def test_set_items(self):
        shelf = self.model.objects.create()
        self.assertEqual(list(shelf.books.all()), [])

        books = self.books[5:2:-1]
        shelf.books = books
        self.assertEqual(list(shelf.books.all()), books)

        books.reverse()
        shelf.books = books
        self.assertEqual(list(shelf.books.all()), books)

        shelf.books.add(self.books[8])
        self.assertEqual(list(shelf.books.all()), books + [self.books[8]])

        shelf.books = []
        self.assertEqual(list(shelf.books.all()), [])

        shelf.books = [self.books[9]]
        self.assertEqual(list(shelf.books.all()), [
            self.books[9]])

        shelf.books = []
        self.assertEqual(list(shelf.books.all()), [])

    def test_set_items_by_pk(self):
        shelf = self.model.objects.create()
        self.assertEqual(list(shelf.books.all()), [])

        books = self.books[5:2:-1]
        shelf.books = [b.pk for b in books]
        self.assertEqual(list(shelf.books.all()), books)

        shelf.books = [self.books[5].pk, self.books[2]]
        self.assertEqual(list(shelf.books.all()), [
            self.books[5],
            self.books[2]])

        shelf.books = [unicode(self.books[8].pk)]
        self.assertEqual(list(shelf.books.all()), [self.books[8]])

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

    def test_remove_items_by_pk(self):
        shelf = self.model.objects.create()
        shelf.books = self.books[2:5]
        self.assertEqual(list(shelf.books.all()), [
            self.books[2],
            self.books[3],
            self.books[4]])

        shelf.books.remove(self.books[3].pk)
        self.assertEqual(list(shelf.books.all()), [
            self.books[2],
            self.books[4]])

        shelf.books.remove(self.books[2], unicode(self.books[4].pk))
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


class TestStringReference(TestSortedManyToManyField):
    '''
    Test the same things as ``TestSortedManyToManyField`` but using a model
    that using a string to reference the relation where the m2m field should
    point to.
    '''
    model = DoItYourselfShelf

    def test_custom_sort_value_field_name(self):
        from sortedm2m.fields import SORT_VALUE_FIELD_NAME

        self.assertEqual(len(self.model._meta.many_to_many), 1)
        sortedm2m = self.model._meta.many_to_many[0]
        intermediate_model = sortedm2m.rel.through

        # make sure that standard sort field is not used
        self.assertRaises(
            FieldDoesNotExist,
            intermediate_model._meta.get_field_by_name,
            SORT_VALUE_FIELD_NAME)

        field = intermediate_model._meta.get_field_by_name('diy_sort_number')
        self.assertTrue(field)


class TestSelfReference(TestCase):
    def test_self_adding(self):
        s1 = SelfReference.objects.create()
        s2 = SelfReference.objects.create()
        s3 = SelfReference.objects.create()
        s4 = SelfReference.objects.create()
        s1.me.add(s3)
        s1.me.add(s4, s2)

        self.assertEquals(list(s1.me.all()), [s3,s4,s2])
