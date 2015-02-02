# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='M2MToSortedM2M',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SortedM2MToM2M',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sortedm2mtom2m',
            name='m2m',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='altersortedmanytomanyfield_tests.Target'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='m2mtosortedm2m',
            name='m2m',
            field=models.ManyToManyField(to='altersortedmanytomanyfield_tests.Target'),
            preserve_default=True,
        ),
    ]
