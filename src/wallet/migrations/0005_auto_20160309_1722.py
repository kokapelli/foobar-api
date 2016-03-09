# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-09 17:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0004_auto_20160309_1721'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='wallet',
            unique_together=set([('owner_id', 'balance_currency')]),
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='currency',
        ),
    ]
