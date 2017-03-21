# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('migrations_tests', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallery',
            name='photos2',
            field=sortedm2m.fields.SortedManyToManyField(
                help_text=None,
                related_name='gallery2+',
                to='migrations_tests.Photo'),
            preserve_default=True,
        ),
    ]
