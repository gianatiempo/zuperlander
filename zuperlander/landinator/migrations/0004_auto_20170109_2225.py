# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-10 01:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landinator', '0003_auto_20170109_2211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formulariodinamico',
            name='facebook_ad_code_list',
            field=models.ManyToManyField(related_name='codes', to='landinator.FacebookAdCode'),
        ),
    ]
