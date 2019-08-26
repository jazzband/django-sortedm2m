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


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    matches = re.search(r"__version__[\s]+=[\s]+['\"](?P<version>[^'\"]+)['\"]",
                        open(os.path.join(package, '__init__.py')).read(),
                        re.M)

    return matches.group(1) if matches else None


def read(filename):
    return codecs.open(os.path.join(os.path.dirname(__file__), filename),
                       encoding='utf8').read()


long_description = '\n\n'.join((
    read('README.rst'),
    read('CHANGES.rst'),
))

setup(
    name='django-sortedm2m',
    version=get_version('sortedm2m'),
    url='http://github.com/jazzband/django-sortedm2m',
    license='BSD',
    description="Drop-in replacement for django's many to many field with sorted relations.",
    long_description=long_description,
    author=u'Gregor Müllegger',
    author_email='gregor@muellegger.de',
    packages=['sortedm2m'],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[
        'six',
    ],
)
