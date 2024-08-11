#!/usr/bin/env python
import os
import sys
import warnings

import django
from django.core.management import execute_from_command_line

parent = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent)

DEFAULT_TEST_APPS = [
    'sortedm2m_tests',
]


def runtests(*args):
    warnings.filterwarnings("ignore", module="distutils")

    test_apps = list(args or DEFAULT_TEST_APPS)
    print([sys.argv[0], 'test', '--verbosity=1'] + test_apps)
    execute_from_command_line([sys.argv[0], 'test', '--verbosity=1'] + test_apps)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
