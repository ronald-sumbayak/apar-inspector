# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-14 04:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20170714_0438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspectionreport',
            name='kondisi',
            field=models.IntegerField(choices=[(1, 'Baik'), (0, 'Tidak Baik')]),
        ),
    ]