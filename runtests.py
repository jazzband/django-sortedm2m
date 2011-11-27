#!/usr/bin/env python
import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
parent = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))

sys.path.insert(0, parent)

from django.test.simple import DjangoTestSuiteRunner


def runtests():
    test_runner = DjangoTestSuiteRunner(
        verbosity=1,
        interactive=True,
        failfast=False)
    failures = test_runner.run_tests([
        'sortedm2m_field',
        'sortedm2m_form',
        'south_support',
    ])
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
