# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CompanyInfo'
        db.create_table('invoices_companyinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='companyinfo', unique=True, to=orm['auth.User'])),
            ('bankaccount', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('inum', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('tinum', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='CZE', max_length=3)),
            ('town', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('phone', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('invoices', ['CompanyInfo'])

        # Adding model 'Invoice'
        db.create_table('invoices_invoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issueDate', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('contractor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='outinvoices', to=orm['invoices.CompanyInfo'])),
            ('subscriber', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ininvoices', to=orm['invoices.CompanyInfo'])),
            ('typee', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('paymentWay', self.gf('django.db.models.fields.IntegerField')()),
            ('paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['valueladder.Thing'])),
        ))
        db.send_create_signal('invoices', ['Invoice'])

        # Adding model 'Item'
        db.create_table('invoices_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['invoices.Invoice'])),
        ))
        db.send_create_signal('invoices', ['Item'])

        # Adding model 'BadIncommingTransfer'
        db.create_table('invoices_badincommingtransfer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['invoices.Invoice'], null=True)),
            ('transactionInfo', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('typee', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('invoices', ['BadIncommingTransfer'])


    def backwards(self, orm):
        # Deleting model 'CompanyInfo'
        db.delete_table('invoices_companyinfo')

        # Deleting model 'Invoice'
        db.delete_table('invoices_invoice')

        # Deleting model 'Item'
        db.delete_table('invoices_item')

        # Deleting model 'BadIncommingTransfer'
        db.delete_table('invoices_badincommingtransfer')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'invoices.badincommingtransfer': {
            'Meta': {'object_name': 'BadIncommingTransfer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoices.Invoice']", 'null': 'True'}),
            'transactionInfo': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'typee': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'invoices.companyinfo': {
            'Meta': {'object_name': 'CompanyInfo'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'bankaccount': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inum': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.IntegerField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'CZE'", 'max_length': '3'}),
            'tinum': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'town': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'companyinfo'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'invoices.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'contractor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outinvoices'", 'to': "orm['invoices.CompanyInfo']"}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['valueladder.Thing']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issueDate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paymentWay': ('django.db.models.fields.IntegerField', [], {}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ininvoices'", 'to': "orm['invoices.CompanyInfo']"}),
            'typee': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'invoices.item': {
            'Meta': {'object_name': 'Item'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['invoices.Invoice']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'price': ('django.db.models.fields.FloatField', [], {})
        },
        'valueladder.thing': {
            'Meta': {'object_name': 'Thing'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['invoices']