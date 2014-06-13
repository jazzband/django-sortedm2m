# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding SortedM2M table for field photos on 'Gallery'
        db.create_table('test_south_support_gallery_photos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gallery', models.ForeignKey(orm['test_south_support.gallery'], null=False)),
            ('photo', models.ForeignKey(orm['test_south_support.photo'], null=False)),
            ('sort_value', models.IntegerField())
        ))
        db.create_unique('test_south_support_gallery_photos', ['gallery_id', 'photo_id'])


    def backwards(self, orm):

        # Removing M2M table for field photos on 'Gallery'
        db.delete_table('test_south_support_gallery_photos')


    models = {
        'test_south_support.gallery': {
            'Meta': {'object_name': 'Gallery'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'photos': ('sortedm2m.fields.SortedManyToManyField', [], {'to': "orm['test_south_support.Photo']", 'symmetrical': 'False'})
        },
        'test_south_support.photo': {
            'Meta': {'object_name': 'Photo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'test_south_support.unsortedgallery': {
            'Meta': {'object_name': 'UnsortedGallery'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'photos': ('sortedm2m.fields.SortedManyToManyField', [], {'sorted': 'False', 'symmetrical': 'False', 'to': "orm['test_south_support.Photo']"})
        }
    }

    complete_apps = ['test_south_support']
