# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-10 05:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wad_Budget', '0002_budget_internalsudsobject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='budget',
            name='internalsudsobject',
        ),
    ]
