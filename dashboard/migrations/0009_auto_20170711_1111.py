# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-11 04:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_auto_20170711_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apar',
            name='kondisi',
            field=models.IntegerField(choices=[(-1, 'Bad'), (0, 'Unknown'), (1, 'Good')], default=0),
        ),
    ]
