#!/usr/bin/env python
import codecs
import os
import re

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    matches = re.search(
        r"__version__[\s]+=[\s]+['\"](?P<version>[^'\"]+)['\"]",
        open(os.path.join(package, '__init__.py')).read(),
        re.M
    )

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
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
