================
django-sortedm2m
================

.. image:: https://travis-ci.org/gregmuellegger/django-sortedm2m.png
   :alt: Build Status
   :target: https://travis-ci.org/gregmuellegger/django-sortedm2m

``sortedm2m`` is a drop-in replacement for django's own ``ManyToManyField``.
The provided ``SortedManyToManyField`` behaves like the original one but
remembers the order of added relations.

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

``SortedManyToManyField``
-------------------------

You can use the following arguments to modify the default behavior:

``sorted``
~~~~~~~~~~

**Default:** ``True``

You can set the ``sorted`` to ``False`` which will force the
``SortedManyToManyField`` in behaving like Django's original
``ManyToManyField``. No ordering will be performed on relation nor will the
intermediate table have a database field for storing ordering information.

``sort_value_field_name``
~~~~~~~~~~~~~~~~~~~~~~~~~

**Default:** ``'sort_value'``

Specifies how the field is called in the intermediate database table by which
the relationship is ordered. You can change its name if you have a legacy
database that you need to integrate into your application.

Admin
=====

``SortedManyToManyField`` provides a custom widget which can be used to sort
the selected items. It renders a list of checkboxes that can be sorted by
drag'n'drop.

To use the widget in the admin you need to add ``sortedm2m`` to your
INSTALLED_APPS settings, like::

   INSTALLED_APPS = (
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.sites',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       'django.contrib.admin',
   
       'sortedm2m',

       '...',
   )

Otherwise it will not find the css and js files needed to sort by drag'n'drop.

Finally, make sure *not* to have the model listed in any ``filter_horizontal``
or ``filter_vertical`` tuples inside of your ``ModelAdmin`` definitions.

If you did it right, you'll wind up with something like this:

.. image:: http://i.imgur.com/9Bjfo7Q.png

It's also possible to use the ``SortedManyToManyField`` with admin's
``raw_id_fields`` option in the ``ModelAdmin`` definition. Add the name of the
``SortedManyToManyField`` to this list to get a simple text input field. The
order in which the ids are entered into the input box is used to sort the
items of the sorted m2m relation.

Example::

    from django.contrib import admin

    class GalleryAdmin(admin.ModelAdmin):
        raw_id_fields = ('photos',)

Contribute
==========

You can find the latest development version on github_. Get there and fork it,
file bugs or send me nice wishes.

Feel free to drop me a message about critique or feature requests. You can get
in touch with me by mail_ or twitter_.

.. _github: http://github.com/gregmuellegger/django-sortedm2m
.. _mail: mailto:gregor@muellegger.de
.. _twitter: http://twitter.com/gregmuellegger
