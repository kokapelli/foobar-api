# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-12 15:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_auto_20170212_1247'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryitem',
            name='received',
            field=models.BooleanField(default=False, help_text='Has the product been received?'),
        ),
    ]