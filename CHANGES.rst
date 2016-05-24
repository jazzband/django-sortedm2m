Changelog
=========

1.3.0
-----

* `#79`_: Use `.sortedm2m-item` selector in the widget's JavaScript code to
  target the list items. This was previously `ul.sortedm2m li`. This improves
  compatibility other markup that does not want to use `ul`/`li` tags. Thanks
  to Michal Dabski for the patch.

  **Note:** If you use custom markup with the JavaScript code, you need to make
  sure that the items now have the `sortedm2m-item` class name.

* `#76`_: Add support for to_field_name to SortedMultipleChoiceField. Thanks
  to Conrad Kramer for the patch.

.. _#76: https://github.com/gregmuellegger/django-sortedm2m/pull/76
.. _#76: https://github.com/gregmuellegger/django-sortedm2m/pull/79

1.2.2
-----

* `#75`_: Fix "add another" admin popup. It didn't refresh the list of items in Django
  1.8+. Thanks to Vadim Sikora for the patch.

.. _#75: https://github.com/gregmuellegger/django-sortedm2m/pull/75

1.2.1
-----

* *skipped*

1.2.0
-----

* Dropping Python 3.2 support. It has reached end of life in February 2016.

1.1.2
-----

* `#71`_: Don't break collectstatic for some cases. Therefore we removed the
  STATIC_URL prefix from the form media definition in
  ``SortedCheckboxSelectMultiple``. Thanks to Kirill Ermolov for the
  patch.

.. _#71: https://github.com/gregmuellegger/django-sortedm2m/issues/71

1.1.1
-----

* `#70`_: CSS fix for Django 1.9 new admin design. Thanks to Maarten Draijer
  for the patch.

.. _#70: https://github.com/gregmuellegger/django-sortedm2m/pull/70

1.1.0
-----

* `#59`_, `#65`_, `#68`_: Django 1.9 support. Thanks to Scott Kyle and Jasper Maes for
  patches.
* `#67`_: Support for disabling migrations for some models, that can be
  decided by Django's DB router (with the ``allow_migrate_model`` method).
  Thanks to @hstanev for the patch.

.. _#59: https://github.com/gregmuellegger/django-sortedm2m/pull/59
.. _#65: https://github.com/gregmuellegger/django-sortedm2m/pull/65
.. _#67: https://github.com/gregmuellegger/django-sortedm2m/pull/67
.. _#68: https://github.com/gregmuellegger/django-sortedm2m/pull/68

1.0.2
-----

* `#56`_: Fix bug where order is wrong after adding objects. That had to do
  with using the ``count`` of the m2m objects for the next ``sort_value``
  value. We now use the corret ``Max`` aggregation to make sure that newly
  added objects will be in order. Thanks to Scott Kyle for the report and
  patch.

.. _#56: https://github.com/gregmuellegger/django-sortedm2m/pull/56

1.0.1
-----

* Performance fix for sorted m2m admin widget. See `#54`_ for details. Thanks
  to Jonathan Liuti for fixing this.

.. _#54: https://github.com/gregmuellegger/django-sortedm2m/pull/54

1.0.0
-----

* Hooray, we officially declare **django-sortedm2m** to be stable and
  promise to be backwards compatible to new releases (we already doing good
  since since the beginning in that regard).
* Django 1.8 support for ``AlterSortedManyToManyField`` operation. Thanks to
  Nicolas Trésegnie for starting the implementation.

0.10.0
------

* The creation of the sortedm2m intermediate model and database table is now
  fully done inside of the ``SortedManyToManyField`` class. That makes it much
  easier to modify the creation of this when creating a custom subclass of this
  field. See `#49`_ for an example usecase.
* Adding support for the custom field arguments like ``sorted`` and
  ``sort_value_field_name`` in Django 1.7 migrations. Thanks to Christian
  Kohlstedde for the patch.

.. _#49: https://github.com/gregmuellegger/django-sortedm2m/issues/49

0.9.5
-----

* Fixing ``setup.py`` when run on a system that does not use UTF-8 as default
  encoding. See `#48`_ for details. Thanks to Richard Mitchell for the patch.

.. _#48: https://github.com/gregmuellegger/django-sortedm2m/pull/48

0.9.4
-----

* Fix: ``SortedMultipleChoiceField`` did not properly report changes of the
  data to ``Form.changed_data``. Thanks to @smcoll for the patch.

0.9.3
-----

* Fix: ``AlterSortedManyToManyField`` operation failed for postgres databases.
* Testing against MySQL databases.

0.9.2
-----

* Fix: ``AlterSortedManyToManyField`` operation failed for many to many fields
  which already contained some data.

0.9.1
-----

* Fix: When using the sortable admin widget, deselecting an item in the list
  had not effect. Thank you to madEng84 for the report and patch!

0.9.0
-----

* Adding ``AlterSortedManyToManyField`` migration operation that allows you to
  migrate from ``ManyToManyField`` to ``SortedManyToManyField`` and vice
  versa. Thanks to Joaquín Pérez for the patch!
* Fix: Supporting migrations in Django 1.7.4.
* Fix: The admin widget is not broken anymore for dynamically added inline
  forms. Thanks to Rubén Díaz for the patch!

0.8.1
-----

* Adding support for Django 1.7 migrations. Thanks to Patryk Hes and Richard
  Barran for their reports.
* Adding czech translations. Thanks to @cuchac for the pull request.

0.8.0
-----

* Adding support for Django 1.7 and dropping support for Django 1.4.

0.7.0
-----

* Adding support for ``prefetch_related()``. Thanks to Marcin Ossowski for
  the idea and patch.

0.6.1
-----

* Correct escaping of *for* attribute in label for the sortedm2m widget. Thanks
  to Mystic-Mirage for the report and fix.

0.6.0 
-----

* Python 3 support!
* Better widget. Thanks to Mike Knoop for the initial patch.

0.5.0
-----

* Django 1.5 support. Thanks to Antti Kaihola for the patches.
* Dropping Django 1.3 support. Please use django-sortedm2m<0.5 if you need to
  use Django 1.3.
* Adding support for a ``sort_value_field_name`` argument in
  ``SortedManyToManyField``. Thanks to Trey Hunner for the idea.

0.4.0
-----

* Django 1.4 support. Thanks to Flavio Curella for the patch.
* south support is only enabled if south is actually in your INSTALLED_APPS
  setting. Thanks to tcmb for the report and Florian Ilgenfritz for the patch.

0.3.3
-----

* South support (via monkeypatching, but anyway... it's there!). Thanks to
  Chris Church for the patch. South migrations won't pick up a changed
  ``sorted`` argument though.

0.3.2
-----

* Use already included jQuery version in global scope and don't override with
  django's version. Thank you to Hendrik van der Linde for reporting this
  issue.

0.3.1
-----

* Fixed packaging error.

0.3.0
-----

* Heavy internal refactorings. These were necessary to solve a problem with
  ``SortedManyToManyField`` and a reference to ``'self'``.

0.2.5
-----

* Forgot to exclude debug print/console.log statements from code. Sorry.

0.2.4
-----

* Fixing problems with ``SortedCheckboxSelectMultiple`` widget, especially in
  admin where a "create and add another item" popup is available.

0.2.3
-----

* Fixing issue with primary keys instead of model instances for ``.add()`` and
  ``.remove()`` methods in ``SortedRelatedManager``.

0.2.2
-----

* Fixing validation error for ``SortedCheckboxSelectMultiple``. It caused
  errors if only one value was passed.

0.2.1
-----

* Removed unnecessary reference of jquery ui css file in
  ``SortedCheckboxSelectMultiple``. Thanks to Klaas van Schelven and Yuwei Yu
  for the hint.

0.2.0
-----

* Added a widget for use in admin.
