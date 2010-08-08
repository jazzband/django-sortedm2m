# -*- coding: utf-8 -*-
from django.test import TestCase
from sortedm2m_tests.models import Book, Shelf, Store, MessyStore


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

        shelf.books.clear()
        self.assertEqual(list(shelf.books.all()), [])

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
