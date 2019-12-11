from unittest.case import skipIf

import django
from django.core.exceptions import FieldDoesNotExist
from django.db import connection
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.encoding import force_str

from sortedm2m.compat import get_field, get_rel
from sortedm2m.fields import SORT_VALUE_FIELD_NAME

from .compat import m2m_set
from .models import Book, DoItYourselfShelf, SelfReference, Shelf, Store, TaggedDoItYourselfShelf


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

        shelf.books.add(self.books[5].pk, force_str(self.books[1].pk))
        self.assertEqual(list(shelf.books.all()), [
            self.books[2],
            self.books[5],
            self.books[1]])

        shelf.books.clear()
        self.assertEqual(list(shelf.books.all()), [])

        shelf.books.add(self.books[3].pk, self.books[1], force_str(self.books[2].pk))
        self.assertEqual(list(shelf.books.all()), [
            self.books[3],
            self.books[1],
            self.books[2]])

    def test_set_items(self):
        shelf = self.model.objects.create()
        self.assertEqual(list(shelf.books.all()), [])

        books = self.books[5:2:-1]
        m2m_set(shelf, "books", books)
        self.assertEqual(list(shelf.books.all()), books)

        books.reverse()
        m2m_set(shelf, "books", books)
        self.assertEqual(list(shelf.books.all()), books)

        shelf.books.add(self.books[8])
        self.assertEqual(list(shelf.books.all()), books + [self.books[8]])

        m2m_set(shelf, "books", [])
        self.assertEqual(list(shelf.books.all()), [])

        m2m_set(shelf, "books", [self.books[9]])
        self.assertEqual(list(shelf.books.all()), [
            self.books[9]])

        m2m_set(shelf, "books", [])
        self.assertEqual(list(shelf.books.all()), [])

    def test_set_items_by_pk(self):
        shelf = self.model.objects.create()
        self.assertEqual(list(shelf.books.all()), [])

        books = self.books[5:2:-1]
        m2m_set(shelf, "books", [b.pk for b in books])
        self.assertEqual(list(shelf.books.all()), books)

        m2m_set(shelf, "books", [self.books[5].pk, self.books[2]])
        self.assertEqual(list(shelf.books.all()), [
            self.books[5],
            self.books[2]])

        m2m_set(shelf, "books", [force_str(self.books[8].pk)])
        self.assertEqual(list(shelf.books.all()), [self.books[8]])

    def test_remove_items(self):
        shelf = self.model.objects.create()
        m2m_set(shelf, "books", self.books[2:5])
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
        m2m_set(shelf, "books", self.books[2:5])
        self.assertEqual(list(shelf.books.all()), [
            self.books[2],
            self.books[3],
            self.books[4]])

        shelf.books.remove(self.books[3].pk)
        self.assertEqual(list(shelf.books.all()), [
            self.books[2],
            self.books[4]])

        shelf.books.remove(self.books[2], force_str(self.books[4].pk))
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

    # to enable population of connection.queries
    @override_settings(DEBUG=True)
    def test_prefetch_related_queries_num(self):
        shelf = self.model.objects.create()
        shelf.books.add(self.books[0])

        shelf = self.model.objects.filter(pk=shelf.pk).prefetch_related('books')[0]
        queries_num = len(connection.queries)
        self.assertEqual(queries_num, len(connection.queries))

    def test_prefetch_related_sorting(self):
        shelf = self.model.objects.create()
        books = [self.books[0], self.books[2], self.books[1]]
        m2m_set(shelf, "books", books)

        shelf = self.model.objects.filter(pk=shelf.pk).prefetch_related('books')[0]

        def get_ids(queryset):
            return [obj.id for obj in queryset]

        self.assertEqual(get_ids(shelf.books.all()), get_ids(books))


class TestStringReference(TestSortedManyToManyField):
    """
    Test the same things as ``TestSortedManyToManyField`` but using a model
    that using a string to reference the relation where the m2m field should
    point to.
    """
    model = Store


class TestCustomBaseClass(TestSortedManyToManyField):
    model = DoItYourselfShelf

    def test_base_class_str(self):
        shelf = self.model.objects.create()
        shelf.books.add(self.books[0])
        through_model = shelf.books.through
        instance = through_model.objects.all()[0]
        self.assertEqual(str(instance), "Relationship to {0}".format(instance.book.name))

    def test_custom_sort_value_field_name(self):
        self.assertEqual(len(self.model._meta.many_to_many), 1)
        sortedm2m = self.model._meta.many_to_many[0]
        intermediate_model = get_rel(sortedm2m).through

        # make sure that standard sort field is not used
        self.assertRaises(
            FieldDoesNotExist,
            get_field,
            intermediate_model, SORT_VALUE_FIELD_NAME)

        field = get_field(intermediate_model, 'diy_sort_number')
        self.assertTrue(field)


@skipIf(django.VERSION < (2, 2), 'RelatedManager._add_items() has new through_defaults argument in Django >= 2.2')
class TestCustomThroughClass(TestSortedManyToManyField):
    model = TaggedDoItYourselfShelf

    def test_base_class_str(self):
        shelf = self.model.objects.create()
        shelf.books.add(self.books[0])
        through_model = shelf.books.through
        instance = through_model.objects.all()[0]
        self.assertEqual(str(instance), "Relationship to {0} tagged as <>".format(instance.book.name))

    def test_through_defaults(self):
        shelf = self.model.objects.create()
        shelf.books.add(*self.books[3:5], through_defaults={'tags': 'A'})
        shelf.books.add(self.books[2])
        shelf.books.add(*self.books[:2], through_defaults={'tags': 'B'})

        # ordering is kept
        self.assertEqual(list(shelf.books.all()),
                         self.books[3:5] + [self.books[2]] + self.books[:2])

        through_model = shelf.books.through
        rels = [(o.book_id, o.tags_diy_sort_number, o.tags) for o in through_model.objects.all()]

        self.assertEqual(rels, [
            (self.books[3].pk, 1, 'A'),
            (self.books[4].pk, 2, 'A'),
            (self.books[2].pk, 3, ''),
            (self.books[0].pk, 4, 'B'),
            (self.books[1].pk, 5, 'B'),
        ])


class TestSelfReference(TestCase):
    def test_self_adding(self):
        s1 = SelfReference.objects.create()
        s2 = SelfReference.objects.create()
        s3 = SelfReference.objects.create()
        s4 = SelfReference.objects.create()
        s1.me.add(s3)
        s1.me.add(s4, s2)

        self.assertEqual(list(s1.me.all()), [s3, s4, s2])
