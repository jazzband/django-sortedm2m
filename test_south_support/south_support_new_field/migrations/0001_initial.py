# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PhotoStream'
        db.create_table('south_support_new_field_photostream', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('south_support_new_field', ['PhotoStream'])


    def backwards(self, orm):
        # Deleting model 'PhotoStream'
        db.delete_table('south_support_new_field_photostream')


    models = {
        'south_support_new_field.photostream': {
            'Meta': {'object_name': 'PhotoStream'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['south_support_new_field']
