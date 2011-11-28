#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import find_packages, setup


class UltraMagicString(object):
    '''
    Taken from
    http://stackoverflow.com/questions/1162338/whats-the-right-way-to-use-unicode-metadata-in-setup-py
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __unicode__(self):
        return self.value.decode('UTF-8')

    def __add__(self, other):
        return UltraMagicString(self.value + str(other))

    def split(self, *args, **kw):
        return self.value.split(*args, **kw)


long_description = UltraMagicString('\n\n'.join((
    file('README.rst').read(),
    file('CHANGES.rst').read(),
)))


# determine package version

sys.path.insert(0, os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'example'))
sys.path.insert(0, os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'src'))

import sortedm2m
version = '.'.join([str(x) for x in sortedm2m.__version__[:3]])

if len(sortedm2m.__version__) > 3:
    version += ''.join([str(x) for x in sortedm2m.__version__[3:]])


setup(
    name = 'django-sortedm2m',
    version = version,
    url = 'http://github.com/gregmuellegger/django-sortedm2m',
    license = 'BSD',
    description =
        'Drop-in replacement for django\'s many to many field with '
        'sorted relations.',
    long_description = long_description,
    author = UltraMagicString('Gregor Müllegger'),
    author_email = 'gregor@muellegger.de',
    packages = ['sortedm2m'],
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires = [],
    tests_require=['Django', 'South', 'django-setuptest'],
    test_suite='sortedm2m_tests.TestSuite',
)

