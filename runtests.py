#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import warnings

parent = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, parent)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")


import django
from django.core.management import execute_from_command_line


default_test_apps = [
    'sortedm2m_tests',
]


def runtests(*args):
    if django.VERSION > (1, 8):
        warnings.simplefilter("error", Warning)
        warnings.filterwarnings("ignore", module="distutils")
        try:
            warnings.filterwarnings("ignore", category=ResourceWarning)
        except NameError:
            pass
        warnings.filterwarnings("ignore", "invalid escape sequence", DeprecationWarning)
        # Ignore a python 3.6 DeprecationWarning in ModelBase.__new__ that isn't
        # fixed in Django 1.x
        if sys.version_info > (3, 6) and django.VERSION < (2,):
            warnings.filterwarnings(
                "ignore", "__class__ not set defining", DeprecationWarning)

    test_apps = list(args or default_test_apps)
    execute_from_command_line([sys.argv[0], 'test', '--verbosity=1'] + test_apps)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
