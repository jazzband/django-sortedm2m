#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os, sys


parent = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, parent)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")


import django
from django.core.management import execute_from_command_line


if django.VERSION < (1, 6):
    default_test_apps = [
        'sortedm2m_tests',
        'test_south_support',
    ]
else:
    default_test_apps = [
        'sortedm2m_tests',
    ]

    # Only test south support for Django 1.6 and lower.
    if django.VERSION < (1, 7):
        default_test_apps += [
            'test_south_support',
        ]


def runtests(*args):
    test_apps = list(args or default_test_apps)
    execute_from_command_line([sys.argv[0], 'test', '--verbosity=1'] + test_apps)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
