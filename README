================
django-sortedm2m
================

``sortedm2m`` is a drop in replacement for django's own ``ManyToManyField``.
The provided ``SortedManyToManyField`` behaves like the original one but
remembers the order of added relations.

``sortedm2m`` requires at least django 1.2. Django 1.1 or earlier is not
supported.

Usecases
========

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
=====

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
=====

``SortedManyToManyField`` provides a custom widget which can be used to sort
the selected items. It renders a list of checkboxes that can be sorted by
drag'n'drop.

It's also possible to use the ``SortedManyToManyField`` with admin's
``raw_id_fields`` option in the ``ModelAdmin`` definition. Add the name of the
``SortedManyToManyField`` to this list to get a simple text input field. The
order in which the ids are entered into the input box is used to sort the
items of the sorted m2m relation.

Example::

    from django.contrib import admin

    class GalleryAdmin(admin.ModelAdmin):
        raw_id_fields = ('photos',)
