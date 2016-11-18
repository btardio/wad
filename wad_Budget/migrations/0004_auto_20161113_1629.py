# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wad_Budget', '0003_remove_budget_internalsudsobject'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='internalbooleansync',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='budget',
            name='budgetamount',
            field=models.BigIntegerField(default=20000000),
        ),
        migrations.AlterField(
            model_name='budget',
            name='budgetdeliverymethod',
            field=models.CharField(default=b'ACCELERATED', max_length=20, choices=[(b'STANDARD', b'Standard'), (b'ACCELERATED', b'Accelerated'), (b'TESTING', b'Testing')]),
        ),
        migrations.AlterField(
            model_name='budget',
            name='budgetname',
            field=models.CharField(help_text=b'Budget name', unique=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='budget',
            name='budgetstatus',
            field=models.CharField(default=b'ENABLED', max_length=20, choices=[(b'ENABLED', b'Enabled'), (b'PAUSED', b'Paused'), (b'REMOVED', b'Removed'), (b'TESTING', b'Testing')]),
        ),
    ]
