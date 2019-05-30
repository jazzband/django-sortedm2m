#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import pytest
from django.core.management import execute_from_command_line


parent = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, parent)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")


def runtests(*args):

    test_apps = list(args or ['sortedm2m_tests'])
    execute_from_command_line([sys.argv[0], 'test', '--verbosity=1'] + test_apps)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
