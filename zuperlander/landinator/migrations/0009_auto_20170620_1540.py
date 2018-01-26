# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-06-20 18:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landinator', '0008_auto_20170202_2054'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='facebookfanpage',
            options={},
        ),
        migrations.AlterField(
            model_name='dynaformfield',
            name='field_name',
            field=models.SlugField(help_text='nombre del campo solo letras minúsculas, guionbajo y numeros ', max_length=200, verbose_name='Identificador del Campo'),
        ),
        migrations.AlterField(
            model_name='facebookfanpage',
            name='fan_page_id',
            field=models.CharField(max_length=200, verbose_name='ID de la Fan Page'),
        ),
        migrations.AlterField(
            model_name='facebookfanpage',
            name='nombre',
            field=models.CharField(max_length=200, verbose_name='Nombre de la Fan Page'),
        ),
        migrations.AlterField(
            model_name='facebookfanpage',
            name='token',
            field=models.CharField(max_length=500, verbose_name='Token de la Fan Page'),
        ),
        migrations.AlterField(
            model_name='formulariodinamico',
            name='adf_recipient',
            field=models.CharField(blank=True, help_text='ej: CRM@dominio.com', max_length=100, verbose_name='Email CRM'),
        ),
        migrations.AlterField(
            model_name='formulariodinamico',
            name='adf_send_email',
            field=models.BooleanField(default=False, verbose_name='Enviar mail ADF'),
        ),
    ]