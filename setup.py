#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import re
import sys
from setuptools import setup


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


if sys.version_info[0] < 3:
    def read(*parts):
        return codecs.open(os.path.join(os.path.dirname(__file__), *parts)).read()

else:
    def read(*parts):
        return open(os.path.join(os.path.dirname(__file__), *parts), 'r').read()


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
    read('README.rst'),
    read('CHANGES.rst'),
)))


setup(
    name = 'django-sortedm2m',
    version = find_version('sortedm2m', '__init__.py'),
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
    install_requires = [],
)
