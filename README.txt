django-sortedm2m
================

``sortedm2m`` is a drop in replacement for django's own ``ManyToManyField``.
The provided ``SortedManyToManyField`` behaves like the original one but
remembers the order of added relations.

Usecases
--------

Imagine that you have a gallery model and a photo model. Usually you want a
relation between these models so you can add multiple photos to one gallery
but also want to be able to have the same photo on many galleries.

This is where you usually can use many to many relation. The downside is that
django's default implementation doesn't provide a way to order the photos in
the gallery. So you only have a random ordering which is not suitable in most
cases.

You can work around this limitation by using the ``SortedManyToManyField``
provided by this package as drop in replacement for django's
``ManyToManyField``.

Usage
-----

Use ``SortedManyToManyField`` like ``ManyToManyField`` in your models::

    from django.db import models
    from sortedm2m.fields import SortedManyToManyField

    class Photo(models.Model):
        name = models.CharField(max_length=50)
        image = models.ImageField(upload_to='...')

    class Gallery(models.Model):
        name = models.CharField(max_length=50)
        photos = SortedManyToManyField(Photo)

If you use the relation in your code like the following, it will remember the
order in which you have added photos to the gallery. ::

    gallery = Gallery.objects.create(name='Photos ordered by name')
    for photo in Photo.objects.order_by('name'):
        gallery.photos.add(photo)

Admin
-----

There is a small caveat with using the sorted m2m relation in django's admin.
Because django renderes many to many relations in a select list by default its
not possible for the ``SortedManyToManyField`` to determine the desired
ordering.

So you have to work around this to use the sorting on models managed by the
admin. You can tell the admin to display a simple input box instead of the
select list where you can then enter raw ids seperated by commas. If you use
that widget you can specify the ordering by changing the order of the ids in
the input box.

Use the ``raw_id_fields`` option in the ``ModelAdmin`` definition for you
model. Example::

    from django.contrib import admin

    class GalleryAdmin(admin.ModelAdmin):
        raw_id_fields = ('photos',)
