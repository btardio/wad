# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-10 04:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wad_Budget', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='internalsudsobject',
            field=models.TextField(blank=True, default=b''),
        ),
    ]
