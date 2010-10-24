#!/usr/bin/env python
import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
parent = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))

sys.path.insert(0, parent)

from django.test.simple import run_tests


def runtests():
    failures = run_tests(
        ['after_model_loaded', 'sortedm2m_field', 'sortedm2m_form'],
        verbosity=1, interactive=True)
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
