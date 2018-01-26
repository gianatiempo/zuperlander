# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-22 22:17
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
import django.db.models.manager
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Adjunto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='')),
            ],
            options={
                'verbose_name_plural': 'Adjuntos',
            },
        ),
        migrations.CreateModel(
            name='DynaFormField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_pk', models.PositiveIntegerField(blank=True, null=True, verbose_name='object PK')),
                ('field_name', models.SlugField(help_text='nombre del campo solo letras minúsculas, guinobajo y numeros ', max_length=200, verbose_name='Identificador del Campo')),
                ('field_label', models.CharField(help_text='nombre visible del campo', max_length=200, verbose_name='Etiqueta del Campo')),
                ('field_type', models.CharField(choices=[('BooleanField', 'BooleanField'), ('CharField', 'CharField'), ('ChoiceField', 'ChoiceField'), ('DateField', 'DateField'), ('DateTimeField', 'DateTimeField'), ('DecimalField', 'DecimalField'), ('EmailField', 'EmailField'), ('FileField', 'FileField'), ('FloatField', 'FloatField'), ('ImageField', 'ImageField'), ('IntegerField', 'IntegerField'), ('RegexField', 'RegexField'), ('SlugField', 'SlugField'), ('TimeField', 'TimeField'), ('URLField', 'URLField'), ('NullBooleanField', 'NullBooleanField'), ('MultipleChoiceField', 'MultipleChoiceField'), ('ModelChoiceField', 'ModelChoiceField'), ('ModelMultipleChoiceField', 'ModelMultipleChoiceField'), ('ReCaptchaField', 'ReCaptchaField')], max_length=100)),
                ('field_widget', models.CharField(blank=True, choices=[('Simple', (('TextInput', 'TextInput'), ('PasswordInput', 'PasswordInput'), ('HiddenInput', 'HiddenInput'), ('DateInput', 'DateInput'), ('DateTimeInput', 'DateTimeInput'), ('TimeInput', 'TimeInput'), ('Textarea', 'Textarea'))), ('Multiples', (('CheckboxInput', 'CheckboxInput'), ('Select', 'Select'), ('SelectSelectedDisableFirst', 'SelectSelectedDisableFirst'), ('NullBooleanSelect', 'NullBooleanSelect'), ('SelectMultiple', 'SelectMultiple'), ('RadioSelect', 'RadioSelect'), ('CheckboxSelectMultiple', 'CheckboxSelectMultiple'))), ('Fechas', (('SplitDateTimeWidget', 'SplitDateTimeWidget'), ('SelectDateWidget', 'SelectDateWidget'), ('HTML5DateWidget', 'HTML5DateWidget'), ('HTML5TimeWidget', 'HTML5TimeWidget'))), ('Archivos/Imagenes', (('FileInput', 'FileInput'), ('ClearableFileInput', 'ClearableFileInput'))), ('Foundation', (('FoundationRadioSelectWidget', 'FoundationRadioSelectWidget'), ('FoundationCheckboxSelectMultipleWidget', 'FoundationCheckboxSelectMultipleWidget'), ('FoundationURLWidget', 'FoundationURLWidget'), ('FoundationImageWidget', 'FoundationImageWidget'), ('FoundationThumbnailWidget', 'FoundationThumbnailWidget')))], max_length=100, null=True)),
                ('field_help', models.CharField(blank=True, max_length=200, verbose_name='Texto descripción')),
                ('is_required', models.BooleanField(default=True, verbose_name='Requerido')),
                ('is_hidden', models.BooleanField(default=False, verbose_name='Oculto')),
                ('default_value', models.CharField(blank=True, help_text='Se pueden usar variables del contexto {{ object }}, {{ sites }}, etc', max_length=200, verbose_name='Valor por defecto')),
                ('choices', models.TextField(blank=True, help_text='Lista de "valor", "título" separada por el delimitador y por línea', verbose_name='Lista de valores')),
                ('choices_delimiter', models.CharField(blank=True, default='|', max_length=1, verbose_name='Delimitador de valores por defecto es |')),
                ('choices_queryset_filter', models.CharField(blank=True, max_length=200, verbose_name='Filtros')),
                ('choices_queryset_empty_label', models.CharField(blank=True, default='------', max_length=100, verbose_name='Valor por defecto')),
                ('choices_queryset_label', models.CharField(blank=True, help_text='puede ser cualquier campo del modelo en formato, "%(nombre)s, %(apellido)s"', max_length=100, verbose_name='Formato')),
                ('field_order', models.PositiveSmallIntegerField(default=1)),
                ('choices_queryset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='Modelo de Datos')),
                ('choices_related_field', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='landinator.DynaFormField')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content_type_set_for_dynaformfield', to='contenttypes.ContentType', verbose_name='content type')),
            ],
            options={
                'ordering': ['field_order'],
            },
        ),
        migrations.CreateModel(
            name='FormularioDinamico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(blank=True, choices=[('af', 'Afrikaans'), ('ar', 'Arabic'), ('ast', 'Asturian'), ('az', 'Azerbaijani'), ('bg', 'Bulgarian'), ('be', 'Belarusian'), ('bn', 'Bengali'), ('br', 'Breton'), ('bs', 'Bosnian'), ('ca', 'Catalan'), ('cs', 'Czech'), ('cy', 'Welsh'), ('da', 'Danish'), ('de', 'German'), ('dsb', 'Lower Sorbian'), ('el', 'Greek'), ('en', 'English'), ('en-au', 'Australian English'), ('en-gb', 'British English'), ('eo', 'Esperanto'), ('es', 'Spanish'), ('es-ar', 'Argentinian Spanish'), ('es-co', 'Colombian Spanish'), ('es-mx', 'Mexican Spanish'), ('es-ni', 'Nicaraguan Spanish'), ('es-ve', 'Venezuelan Spanish'), ('et', 'Estonian'), ('eu', 'Basque'), ('fa', 'Persian'), ('fi', 'Finnish'), ('fr', 'French'), ('fy', 'Frisian'), ('ga', 'Irish'), ('gd', 'Scottish Gaelic'), ('gl', 'Galician'), ('he', 'Hebrew'), ('hi', 'Hindi'), ('hr', 'Croatian'), ('hsb', 'Upper Sorbian'), ('hu', 'Hungarian'), ('ia', 'Interlingua'), ('id', 'Indonesian'), ('io', 'Ido'), ('is', 'Icelandic'), ('it', 'Italian'), ('ja', 'Japanese'), ('ka', 'Georgian'), ('kk', 'Kazakh'), ('km', 'Khmer'), ('kn', 'Kannada'), ('ko', 'Korean'), ('lb', 'Luxembourgish'), ('lt', 'Lithuanian'), ('lv', 'Latvian'), ('mk', 'Macedonian'), ('ml', 'Malayalam'), ('mn', 'Mongolian'), ('mr', 'Marathi'), ('my', 'Burmese'), ('nb', 'Norwegian Bokmål'), ('ne', 'Nepali'), ('nl', 'Dutch'), ('nn', 'Norwegian Nynorsk'), ('os', 'Ossetic'), ('pa', 'Punjabi'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('pt-br', 'Brazilian Portuguese'), ('ro', 'Romanian'), ('ru', 'Russian'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('sq', 'Albanian'), ('sr', 'Serbian'), ('sr-latn', 'Serbian Latin'), ('sv', 'Swedish'), ('sw', 'Swahili'), ('ta', 'Tamil'), ('te', 'Telugu'), ('th', 'Thai'), ('tr', 'Turkish'), ('tt', 'Tatar'), ('udm', 'Udmurt'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('vi', 'Vietnamese'), ('zh-hans', 'Simplified Chinese'), ('zh-hant', 'Traditional Chinese')], max_length=20)),
                ('name', models.CharField(max_length=100, verbose_name='Nombre del form')),
                ('slug', models.SlugField(max_length=100)),
                ('is_active', models.BooleanField(default=True, help_text='activa para usar en el frontend', verbose_name='Es activo')),
                ('form_title', models.CharField(max_length=200, verbose_name='Título del form')),
                ('limite_envios', models.IntegerField(default=-1, help_text='Ingrese la cantidad de formularios completados que se enviaran por mail o -1 para no limitarlo')),
                ('envios', models.IntegerField(default=0)),
                ('send_email', models.BooleanField(default=True, verbose_name='Enviar mail')),
                ('from_email', models.CharField(blank=True, default='webmaster@localhost', max_length=100)),
                ('recipient_list', models.TextField(blank=True, help_text='ej: lista separada por líneas y coma.<br>Juan Pérez, juanperez@dominio.com<br>Maria Gomez, mariagomez@dominio.com', verbose_name='Lista de destinatarios')),
                ('error_class', models.CharField(default='error', max_length=40, verbose_name='Clase CSS para error')),
                ('required_css_class', models.CharField(default='required', max_length=40, verbose_name='Clase CSS para requerido')),
                ('adf_send_email', models.BooleanField(default=True, verbose_name='Enviar mail ADF')),
                ('adf_from_email', models.CharField(blank=True, default='webmaster@localhost', max_length=100)),
                ('adf_recipient', models.CharField(blank=True, help_text='ej: CRM default, CRM@dominio.com', max_length=100, verbose_name='Email CRM')),
                ('autorespond', models.BooleanField(default=False, verbose_name='Autoresponder')),
                ('autorespond_email_field', models.CharField(default='email', max_length=40, verbose_name='Campo de email')),
            ],
            options={
                'verbose_name_plural': '01 Formularios Dinamicos',
                'verbose_name': '01 Formulario Dinamico',
            },
            managers=[
                ('objects_for_admin', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Imagen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='')),
            ],
            options={
                'verbose_name_plural': 'Imagenes',
            },
        ),
        migrations.CreateModel(
            name='Landing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, verbose_name='Landing')),
                ('slug', models.CharField(max_length=100)),
                ('html', models.TextField(verbose_name='HTML del Template')),
                ('google_code', models.TextField(blank=True, null=True)),
                ('google_conversion_code', models.TextField(blank=True, null=True)),
                ('facebook_code', models.TextField(blank=True, null=True)),
                ('facebook_conversion_code', models.TextField(blank=True, null=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='landinator.FormularioDinamico')),
            ],
            options={
                'verbose_name_plural': '03 Landings',
                'verbose_name': '03 Landing',
                'get_latest_by': 'modified',
            },
        ),
        migrations.CreateModel(
            name='TemplateFormularioDinamico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(blank=True, choices=[('af', 'Afrikaans'), ('ar', 'Arabic'), ('ast', 'Asturian'), ('az', 'Azerbaijani'), ('bg', 'Bulgarian'), ('be', 'Belarusian'), ('bn', 'Bengali'), ('br', 'Breton'), ('bs', 'Bosnian'), ('ca', 'Catalan'), ('cs', 'Czech'), ('cy', 'Welsh'), ('da', 'Danish'), ('de', 'German'), ('dsb', 'Lower Sorbian'), ('el', 'Greek'), ('en', 'English'), ('en-au', 'Australian English'), ('en-gb', 'British English'), ('eo', 'Esperanto'), ('es', 'Spanish'), ('es-ar', 'Argentinian Spanish'), ('es-co', 'Colombian Spanish'), ('es-mx', 'Mexican Spanish'), ('es-ni', 'Nicaraguan Spanish'), ('es-ve', 'Venezuelan Spanish'), ('et', 'Estonian'), ('eu', 'Basque'), ('fa', 'Persian'), ('fi', 'Finnish'), ('fr', 'French'), ('fy', 'Frisian'), ('ga', 'Irish'), ('gd', 'Scottish Gaelic'), ('gl', 'Galician'), ('he', 'Hebrew'), ('hi', 'Hindi'), ('hr', 'Croatian'), ('hsb', 'Upper Sorbian'), ('hu', 'Hungarian'), ('ia', 'Interlingua'), ('id', 'Indonesian'), ('io', 'Ido'), ('is', 'Icelandic'), ('it', 'Italian'), ('ja', 'Japanese'), ('ka', 'Georgian'), ('kk', 'Kazakh'), ('km', 'Khmer'), ('kn', 'Kannada'), ('ko', 'Korean'), ('lb', 'Luxembourgish'), ('lt', 'Lithuanian'), ('lv', 'Latvian'), ('mk', 'Macedonian'), ('ml', 'Malayalam'), ('mn', 'Mongolian'), ('mr', 'Marathi'), ('my', 'Burmese'), ('nb', 'Norwegian Bokmål'), ('ne', 'Nepali'), ('nl', 'Dutch'), ('nn', 'Norwegian Nynorsk'), ('os', 'Ossetic'), ('pa', 'Punjabi'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('pt-br', 'Brazilian Portuguese'), ('ro', 'Romanian'), ('ru', 'Russian'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('sq', 'Albanian'), ('sr', 'Serbian'), ('sr-latn', 'Serbian Latin'), ('sv', 'Swedish'), ('sw', 'Swahili'), ('ta', 'Tamil'), ('te', 'Telugu'), ('th', 'Thai'), ('tr', 'Turkish'), ('tt', 'Tatar'), ('udm', 'Udmurt'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('vi', 'Vietnamese'), ('zh-hans', 'Simplified Chinese'), ('zh-hant', 'Traditional Chinese')], max_length=20)),
                ('name', models.CharField(help_text='ej: Subject Contacto', max_length=100, verbose_name='Nombre del template')),
                ('slug', models.SlugField(max_length=100)),
                ('html', models.TextField(help_text='parsea del contexto, y templatetags', verbose_name='HTML del Template')),
                ('is_plain', models.BooleanField(default=True)),
                ('site', models.ManyToManyField(blank=True, related_name='landinator_templateformulariodinamico_related', to='sites.Site')),
            ],
            options={
                'verbose_name_plural': '02 Templates Formularios Dinamicos',
                'verbose_name': '02 Template Formulario Dinamico',
            },
            managers=[
                ('objects_for_admin', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='TrackingFormularioDinamico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de creación')),
                ('lang', models.CharField(choices=[('af', 'Afrikaans'), ('ar', 'Arabic'), ('ast', 'Asturian'), ('az', 'Azerbaijani'), ('bg', 'Bulgarian'), ('be', 'Belarusian'), ('bn', 'Bengali'), ('br', 'Breton'), ('bs', 'Bosnian'), ('ca', 'Catalan'), ('cs', 'Czech'), ('cy', 'Welsh'), ('da', 'Danish'), ('de', 'German'), ('dsb', 'Lower Sorbian'), ('el', 'Greek'), ('en', 'English'), ('en-au', 'Australian English'), ('en-gb', 'British English'), ('eo', 'Esperanto'), ('es', 'Spanish'), ('es-ar', 'Argentinian Spanish'), ('es-co', 'Colombian Spanish'), ('es-mx', 'Mexican Spanish'), ('es-ni', 'Nicaraguan Spanish'), ('es-ve', 'Venezuelan Spanish'), ('et', 'Estonian'), ('eu', 'Basque'), ('fa', 'Persian'), ('fi', 'Finnish'), ('fr', 'French'), ('fy', 'Frisian'), ('ga', 'Irish'), ('gd', 'Scottish Gaelic'), ('gl', 'Galician'), ('he', 'Hebrew'), ('hi', 'Hindi'), ('hr', 'Croatian'), ('hsb', 'Upper Sorbian'), ('hu', 'Hungarian'), ('ia', 'Interlingua'), ('id', 'Indonesian'), ('io', 'Ido'), ('is', 'Icelandic'), ('it', 'Italian'), ('ja', 'Japanese'), ('ka', 'Georgian'), ('kk', 'Kazakh'), ('km', 'Khmer'), ('kn', 'Kannada'), ('ko', 'Korean'), ('lb', 'Luxembourgish'), ('lt', 'Lithuanian'), ('lv', 'Latvian'), ('mk', 'Macedonian'), ('ml', 'Malayalam'), ('mn', 'Mongolian'), ('mr', 'Marathi'), ('my', 'Burmese'), ('nb', 'Norwegian Bokmål'), ('ne', 'Nepali'), ('nl', 'Dutch'), ('nn', 'Norwegian Nynorsk'), ('os', 'Ossetic'), ('pa', 'Punjabi'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('pt-br', 'Brazilian Portuguese'), ('ro', 'Romanian'), ('ru', 'Russian'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('sq', 'Albanian'), ('sr', 'Serbian'), ('sr-latn', 'Serbian Latin'), ('sv', 'Swedish'), ('sw', 'Swahili'), ('ta', 'Tamil'), ('te', 'Telugu'), ('th', 'Thai'), ('tr', 'Turkish'), ('tt', 'Tatar'), ('udm', 'Udmurt'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('vi', 'Vietnamese'), ('zh-hans', 'Simplified Chinese'), ('zh-hant', 'Traditional Chinese')], default='en-us', max_length=20)),
                ('sender', models.CharField(max_length=200)),
                ('utm_source', models.CharField(blank=True, max_length=200, null=True)),
                ('utm_medium', models.CharField(blank=True, max_length=200, null=True)),
                ('utm_campaign', models.CharField(blank=True, max_length=200, null=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('sent_by_mail', models.BooleanField(default=False)),
                ('object_form', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='landinator.FormularioDinamico')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sites.Site')),
            ],
        ),
        migrations.AddField(
            model_name='imagen',
            name='landing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagenes', to='landinator.Landing', verbose_name='landing'),
        ),
        migrations.AddField(
            model_name='formulariodinamico',
            name='adf_body_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dynaform_adf_body_template_related', to='landinator.TemplateFormularioDinamico'),
        ),
        migrations.AddField(
            model_name='formulariodinamico',
            name='adf_subject_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dynaform_adf_subject_template_related', to='landinator.TemplateFormularioDinamico'),
        ),
        migrations.AddField(
            model_name='formulariodinamico',
            name='autorespond_body_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dynaform_autorespond_body_template_related', to='landinator.TemplateFormularioDinamico'),
        ),
        migrations.AddField(
            model_name='formulariodinamico',
            name='autorespond_subject_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dynaform_autorespond_subject_template_related', to='landinator.TemplateFormularioDinamico'),
        ),
        migrations.AddField(
            model_name='formulariodinamico',
            name='body_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dynaform_body_template_related', to='landinator.TemplateFormularioDinamico'),
        ),
        migrations.AddField(
            model_name='formulariodinamico',
            name='form_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dynaform_form_template_related', to='landinator.TemplateFormularioDinamico'),
        ),
        migrations.AddField(
            model_name='formulariodinamico',
            name='site',
            field=models.ManyToManyField(blank=True, related_name='landinator_formulariodinamico_related', to='sites.Site'),
        ),
        migrations.AddField(
            model_name='formulariodinamico',
            name='subject_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dynaform_subject_template_related', to='landinator.TemplateFormularioDinamico'),
        ),
        migrations.AddField(
            model_name='adjunto',
            name='landing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adjuntos', to='landinator.Landing', verbose_name='landing'),
        ),
        migrations.CreateModel(
            name='TrackingEnviado',
            fields=[
            ],
            options={
                'verbose_name_plural': '04 Tracking Formularios Enviados Por Email',
                'proxy': True,
                'verbose_name': '04 Tracking Formulario Enviado Por Email',
            },
            bases=('landinator.trackingformulariodinamico',),
        ),
        migrations.CreateModel(
            name='TrackingNoEnviado',
            fields=[
            ],
            options={
                'verbose_name_plural': '05 Tracking Formularios No Enviados Por Email',
                'proxy': True,
                'verbose_name': '05 Tracking Formulario No Enviado Por Email',
            },
            bases=('landinator.trackingformulariodinamico',),
        ),
    ]
