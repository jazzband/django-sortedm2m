# -*- coding: utf-8 -*-
import sys
from StringIO import StringIO

from django.db import connection
from django.db.models.fields import FieldDoesNotExist
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import six


str_ = six.text_type


class TestMigrateCommand(TestCase):
    def setUp(self):
        sys.stdout = StringIO()
        self.orig_stdout = sys.stdout

    def tearDown(self):
        sys.stdout = self.orig_stdout

    def test_migrate(self):
        call_command('migrate', interactive=False)
