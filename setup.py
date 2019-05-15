#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import re
import sys
from setuptools import setup


PY2 = sys.version_info[0] == 2


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    matches = re.search("__version__[\s]+=[\s]+['\"](?P<version>[^'\"]+)['\"]",
                        open(os.path.join(package, '__init__.py')).read(),
                        re.M)

    return matches.group(1) if matches else None


def read(filename):
    return codecs.open(os.path.join(os.path.dirname(__file__), filename),
                       encoding='utf8').read()

# class UltraMagicString(object):
#     '''
#     Taken from
#     http://stackoverflow.com/questions/1162338/whats-the-right-way-to-use-unicode-metadata-in-setup-py
#     '''
#     def __init__(self, value):
#         if not isinstance(value, bytes):
#             value = value.encode('utf8')
#         self.value = value
# 
#     def __bytes__(self):
#         return self.value
# 
#     def __unicode__(self):
#         return self.value.decode('UTF-8')
# 
#     if sys.version_info[0] < 3:
#         __str__ = __bytes__
#     else:
#         __str__ = __unicode__
# 
#     def __add__(self, other):
#         return UltraMagicString(self.value + bytes(other))
# 
#     def split(self, *args, **kw):
#         return str(self).split(*args, **kw)


long_description = '\n\n'.join((
    read('README.rst'),
    read('CHANGES.rst'),
))

setup(
    name = 'django-sortedm2m',
    version = get_version('sortedm2m'),
    url = 'http://github.com/gregmuellegger/django-sortedm2m',
    license = 'BSD',
    description =
        'Drop-in replacement for django\'s many to many field with '
        'sorted relations.',
    long_description = long_description,
    author = u'Gregor Müllegger',
    author_email = 'gregor@muellegger.de',
    packages = ['sortedm2m'],
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires = [],
)
