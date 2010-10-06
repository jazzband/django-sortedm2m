Changelog
=========

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
