Changelog
=========

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
