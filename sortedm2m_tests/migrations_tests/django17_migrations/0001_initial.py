# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Photo',
                'verbose_name_plural': 'Photos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Photo',
                'verbose_name_plural': 'Photos',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='gallery',
            name='photos',
            field=sortedm2m.fields.SortedManyToManyField(to='migrations_tests.Photo'),
            preserve_default=True,
        ),
    ]
