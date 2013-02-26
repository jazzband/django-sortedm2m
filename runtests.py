#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os, sys


parent = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, parent)
sys.path.insert(0, os.path.join(parent, 'test_project'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from django.core.management import call_command


def runtests(*args):
    test_apps = args or [
        'sortedm2m_tests',
        'sortedm2m_field',
        'sortedm2m_form',
        'south_support',
    ]
    call_command('test', *test_apps)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
