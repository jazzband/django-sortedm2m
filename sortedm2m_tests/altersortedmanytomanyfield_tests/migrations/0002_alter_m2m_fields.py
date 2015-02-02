# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedm2m.fields
import sortedm2m.operations


class Migration(migrations.Migration):

    dependencies = [
        ('altersortedmanytomanyfield_tests', '0001_initial'),
    ]

    operations = [
        sortedm2m.operations.AlterSortedManyToManyField(
            model_name='m2mtosortedm2m',
            name='m2m',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='altersortedmanytomanyfield_tests.Target'),
            preserve_default=True,
        ),
        sortedm2m.operations.AlterSortedManyToManyField(
            model_name='sortedm2mtom2m',
            name='m2m',
            field=models.ManyToManyField(to='altersortedmanytomanyfield_tests.Target'),
            preserve_default=True,
        ),
    ]
