#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os, sys


parent = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, parent)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")


import django
from django.core.management import call_command


if django.VERSION < (1, 6):
    default_test_apps = [
        'sortedm2m_tests',
        'sortedm2m_field',
        'sortedm2m_form',
        'south_support',
        'south_support_new_model',
        'south_support_new_field',
        'south_support_custom_sort_field_name',
    ]
else:
    default_test_apps = [
        'sortedm2m_tests.sortedm2m_field',
        'sortedm2m_tests.sortedm2m_form',
        'sortedm2m_tests.south_support',
        'sortedm2m_tests.south_support.south_support_new_model',
        'sortedm2m_tests.south_support.south_support_new_field',
        'sortedm2m_tests.south_support.south_support_custom_sort_field_name',
    ]


def runtests(*args):
    test_apps = args or default_test_apps
    call_command('test', *test_apps, verbosity=1)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
