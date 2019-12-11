from django.db import models

from sortedm2m.fields import SortedManyToManyField


class BaseBookThrough(object):  # pylint: disable=useless-object-inheritance

    def __str__(self):
        return "Relationship to {0}".format(self.book.name)  # pylint: disable=no-member


class Shelf(models.Model):
    books = SortedManyToManyField('Book', related_name='shelves', base_class=BaseBookThrough)


class Book(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class DoItYourselfShelf(models.Model):
    books = SortedManyToManyField(
        Book,
        sort_value_field_name='diy_sort_number',
        related_name='diy_shelves',
        base_class=BaseBookThrough
    )


class TaggedDoItYourselfShelf(models.Model):
    books = SortedManyToManyField(
        Book,
        sort_value_field_name='diy_sort_number',
        related_name='tagged_diy_shelves',
        through='TagThrough',
        through_fields=('shelf', 'book')
    )


class TagThrough(models.Model):
    _sort_field_name = 'tags_diy_sort_number'

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    shelf = models.ForeignKey(TaggedDoItYourselfShelf, on_delete=models.CASCADE)
    tags = models.CharField(max_length=50, blank=True, default='')
    tags_diy_sort_number = models.IntegerField(default=0)

    def __str__(self):
        return "Relationship to {0} tagged as <{1}>".format(self.book.name, self.tags)


class Store(models.Model):
    books = SortedManyToManyField('sortedm2m_tests.Book', related_name='stores')


class MessyStore(models.Model):
    books = SortedManyToManyField(
        'Book',
        sorted=False,
        related_name='messy_stores'
    )


class SelfReference(models.Model):
    me = SortedManyToManyField('self', related_name='hide+')

    def __str__(self):
        return str(self.pk)
