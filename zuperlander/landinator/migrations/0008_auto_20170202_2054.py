# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-02 23:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landinator', '0007_auto_20170202_2046'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='facebookfanpage',
            options={'verbose_name': '06 Fan Page', 'verbose_name_plural': '06 Fan Pages'},
        ),
        migrations.AlterField(
            model_name='facebookfanpage',
            name='token',
            field=models.CharField(max_length=200, verbose_name='Token de la Fan Page'),
        ),
    ]
