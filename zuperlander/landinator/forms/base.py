import datetime
import io as stringIO
import json
import logging
import os
import re
import uuid

import requests
from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.forms import extras
from django.template import Template
from django.utils.encoding import force_text

from landinator.forms import fields as dynaform_fields
from landinator.forms import widgets as dynaform_widgets
from landinator.models.formulario_dinamico_tracking import TrackingFormularioDinamico

log = logging.getLogger(__name__)

TOKEN_FORMAT = re.compile('%\((?P<field>[a-z0-9\.\_\-]+)\)s', re.U | re.I)


################################################################################
# Base Model DynaForm
################################################################################

class DynaFormClassForm(forms.Form):
    def _resolve_variable(self, variable):
        var_tpl = Template(variable)
        return var_tpl.render(self.get_context())

    def __init__(self, *args, **kwargs):
        object_form = kwargs.pop('object_form', 0)  # Objeto FormularioDinamico
        success_url = kwargs.pop('success_url', '')  # Objeto FormularioDinamico
        request = kwargs.pop('request', 0)  # request
        context = kwargs.pop('context', 0)  # context

        super(DynaFormClassForm, self).__init__(*args, **kwargs)

        self.error_css_class = object_form.error_class
        self.required_css_class = object_form.required_css_class

        for field in object_form.get_fields():
            # configura el field y widget
            try:
                _field = getattr(dynaform_fields, field.field_type)
            except AttributeError:
                _field = getattr(forms, field.field_type)

            field_args = {'label': field.field_label, 'required': field.is_required}

            # set default decimal and float position
            if field.field_type == "DecimalField":
                field_args.update({'decimal_places': 2, 'localize': True})

            if field.default_value:
                # Add context to render fields with context values
                default_value = Template(field.default_value)
                field_args.update({'initial': default_value.render(context)})

            if field.field_help:
                field_args.update({'help_text': field.field_help})

            if field.choices:
                """
                Split key, values
                """
                choices_delimiter = (field.choices_delimiter.strip('\n\r')).strip(' ')
                choices = stringIO.StringIO(field.choices)
                choice_list = []
                choice_list.append(('', 'Seleccionar ' + field.field_label.capitalize()),)

                for choice in choices.readlines():
                    value, label = choice.split(choices_delimiter)
                    choice_list.append(
                        (force_text((value.strip('\n\r')).strip(' ')), force_text((label.strip('\n\r')).strip(' ')),)
                    )

                field_args.update({'choices': choice_list})

            ################################################################
            # Si el queryset es desde un modelo
            ################################################################
            if field.choices_queryset and field.field_type in \
                ("ModelChoiceField", "ModelMultipleChoiceField"):

                qs = field.choices_queryset_queryset()

                # Si tiene una label custom genera la subclase y el metodo
                if field.choices_queryset_label:

                    class CustomModelChoiceField(_field):
                        def label_from_instance(self, obj):
                            key_fields = TOKEN_FORMAT.findall(field.choices_queryset_label)
                            ret = {}
                            for key in key_fields:
                                parts = key.split('__')
                                val = obj
                                for part in parts:
                                    val = getattr(val, part, '')
                                    ret.update({key: val})

                            return field.choices_queryset_label % ret

                    _field = CustomModelChoiceField

                # Si tiene un field relacionado genera los attrs para el
                # handler en javascript
                if field.choices_related_field:
                    class CustomModelChoiceField(_field):
                        _choices = (
                            ('', '------'),
                        )

                        def widget_attrs(self, widget):
                            attrs = super(CustomModelChoiceField, self).widget_attrs(widget)

                            action = reverse('dynaform_choices_related_queryset', kwargs={
                                'field_pk': field.choices_related_field.pk,
                                'related_field_pk': field.pk,
                                'pk': 0
                            })

                            attrs.update({
                                'data-related-field': '',
                                'data-related-field-options': 'action:%(action)s;field:%(field)s;related_field:%(related_field)s;ids:id_%(ids)s;names:%(names)s' % {
                                    'action': action,
                                    'field': field.choices_related_field.pk,
                                    'related_field': field.pk,
                                    'ids': field.choices_related_field.field_name,
                                    'names': field.choices_related_field.field_name
                                },
                            })

                            return attrs

                    # FIXME: Si es un campo relacionado por defecto deja el query
                    # vacio para ser llenado al cambiar el parent
                    # qs = qs.none()

                    _field = CustomModelChoiceField

                field_args.update({
                    'queryset': qs,
                    'empty_label': field.choices_queryset_empty_label
                })

            if field.is_hidden:
                field_args.update({'widget': forms.HiddenInput})

            if field.field_widget:
                attrs = {'placeholder': field.field_help or field.field_label, 'required': field.is_required}
                try:
                    widget = getattr(forms, field.field_widget)(attrs=attrs)
                except AttributeError:
                    try:
                        widget = getattr(extras, field.field_widget)(attrs=attrs)
                    except AttributeError:
                        widget = getattr(dynaform_widgets, field.field_widget)(attrs=attrs)

                field_args.update({'widget': widget})

            self.fields[field.field_name] = _field(**field_args)

        if 'instance' not in kwargs:
            # resuelve el content type y object pk
            if context.get('object'):
                _ct = Template("{% load dynaform_tags %}{{ object|get_ct_pk }}")
                _ct_val = _ct.render(context)
                _pk = Template("{{ object.pk }}")
                _pk_val = _pk.render(context)
            else:
                _ct_val = request.POST.get('_obj_ct')
                _pk_val = request.POST.get('_obj_pk')

            if not '_object_form_pk' in self.fields:
                self.fields['_object_form_pk'] = forms.IntegerField(initial=object_form.pk, required=False,
                                                                    widget=forms.HiddenInput)

            if not '_object_form_success_url' in self.fields:
                self.fields['_object_form_success_url'] = forms.CharField(initial=success_url, required=False,
                                                                          widget=forms.HiddenInput)

            if not '_obj_ct' in self.fields:
                self.fields['_obj_ct'] = forms.IntegerField(initial=_ct_val, required=False, widget=forms.HiddenInput)

            if not '_obj_pk' in self.fields:
                self.fields['_obj_pk'] = forms.IntegerField(initial=_pk_val, required=False, widget=forms.HiddenInput)

            if not '_obj_pk' in self.fields:
                self.fields['_obj_pk'] = forms.IntegerField(initial=_pk_val, required=False, widget=forms.HiddenInput)

            # variables de seguimiento
            if not 'utm_source' in self.fields:
                self.fields['utm_source'] = forms.CharField(initial=request.GET.get('utm_source'), required=False,
                                                            widget=forms.HiddenInput)

            if not 'utm_medium' in self.fields:
                self.fields['utm_medium'] = forms.CharField(initial=request.GET.get('utm_medium'), required=False,
                                                            widget=forms.HiddenInput)

            if not 'utm_campaign' in self.fields:
                self.fields['utm_campaign'] = forms.CharField(initial=request.GET.get('utm_campaign'), required=False,
                                                              widget=forms.HiddenInput)

            geo_data = self.get_location(request)

            if not 'geo_data_city' in self.fields:
                self.fields['geo_data_city'] = forms.CharField(initial=geo_data.get('city'), required=False,
                                                               widget=forms.HiddenInput)

            if not 'geo_data_country' in self.fields:
                self.fields['geo_data_country'] = forms.CharField(initial=geo_data.get('country'), required=False,
                                                                  widget=forms.HiddenInput)

            if not 'geo_data_lat' in self.fields:
                self.fields['geo_data_lat'] = forms.CharField(initial=geo_data.get('lat'), required=False,
                                                              widget=forms.HiddenInput)

            if not 'geo_data_lon' in self.fields:
                self.fields['geo_data_lon'] = forms.CharField(initial=geo_data.get('lon'), required=False,
                                                              widget=forms.HiddenInput)

            if not 'referrer' in self.fields:
                self.fields['referrer'] = forms.CharField(initial='', required=False, widget=forms.HiddenInput)

            ip = self.get_client_ip(request)

            if not 'ip' in self.fields:
                self.fields['ip'] = forms.CharField(initial=ip, required=False, widget=forms.HiddenInput)

        self.object_form = object_form
        self.request = request
        self.context = context
        self.file_fields = {}

    def get_context(self):
        for file_field in self.file_fields.keys():
            self.cleaned_data[file_field] = self.file_fields[file_field]

        self.context.update(
            dict(self.cleaned_data, form=self, site=Site.objects.get_current(), form_title=self.object_form.form_title))

        # add para el doble form
        # si por llega el key ``_dt`` entonces busca ese TrackingFormularioDinamico y
        # lo agrega al contexto dentro de dt

        if self.cleaned_data.get('_dt'):
            _dt = self.cleaned_data.get('_dt')
            dt = TrackingFormularioDinamico.objects.get(pk=_dt)
            try:
                self.context.update({'dt': json.loads(dt.data)})
            except:
                # si falla ahí termina
                pass

        if not self.context.get('object', None) and self.cleaned_data.get('_obj_ct') and self.cleaned_data.get('_obj_pk'):
            object_form_pk = self.cleaned_data['_object_form_pk']
            object_form_success_url = self.cleaned_data['_object_form_success_url']
            obj_ct = self.cleaned_data['_obj_ct']
            obj_pk = self.cleaned_data['_obj_pk']

            try:
                ct = ContentType.objects.get(pk=obj_ct)
            except ContentType.DoesNotExist:
                return self.context

            try:
                obj = ct.get_object_for_this_type(pk=obj_pk)
            except ct.DoesNotExist:
                return self.context

            self.context.update({'object': obj})
            print("update object con", obj)

        return self.context

    def get_recipient_list(self):
        """
        Lee linea a linea buscando una tupla `nombre`,`email`.
        Si encuentra en el incio de la linea un doble corchete `{{` lo trata como un template
        e intenta hacer un `render_to_sting` incluyendo el contexto del objeto.
        Si la primer linea tiene al flag `#alternate` alterna el envio de mails
        """
        recipients = stringIO.StringIO(self.object_form.recipient_list)
        recipient_lines = [line.strip('\n\r') for line in recipients.readlines()]
        recipient_list = []
        alternate = False

        for index, line in enumerate(recipient_lines):
            recipient = line.strip('\n\r')

            ##################################################################
            # Alterna entre diferentes mails el envio
            ##################################################################
            if line == "#alternate":
                alternate = True
                alternate_index = index
                # Guarda el index para sber desde donde intercambiar y
                # devuelve solo el primero
                continue

            ##################################################################
            # Nuevo, si es una variable del template la resuelve {{ object }}
            ##################################################################

            # bug: si tiene un espacio luego de la coma no hace el split
            # name, email = recipient.split(',')
            name, email = re.split('\s*,\s*', recipient)

            if name.startswith('{{'):
                name = self._resolve_variable(name)
                # print "es una variable, intenta resolverla %s" % name

            if email.startswith('{{'):
                email = self._resolve_variable(email)
                # print "es una variable, intenta resolverla %s" % email

            recipient_list.append(
                force_text((email.strip('\n\r')).strip(' '))
            )

        if alternate:
            # Pasa el item del index al final y pone en el lugar el #alternate
            alternate_item = recipient_lines.pop(alternate_index)
            alternate_item = recipient_lines.pop(alternate_index)

            # manda el item al final
            recipient_lines.append(alternate_item)
            recipient_lines.insert(alternate_index, "#alternate")

            # actualiza la DB
            self.object_form.recipient_list = "\n".join(recipient_lines)
            self.object_form.save()
            print(recipient_list[:alternate_index + 1])
            return recipient_list[:alternate_index + 1]

        return recipient_list

    def handle_uploaded_file(self, file, file_field):
        upload_path = os.path.join(settings.MEDIA_ROOT, 'dynaform_uploads', self.object_form.slug)
        file_name = uuid.uuid1().hex
        file_extension = os.path.splitext(file.name)[1]

        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        if file:
            if not file_extension.startswith('.'):
                file_extension = "." + file_extension

            destination = open(upload_path + '/' + file_name + file_extension, 'wb+')
            for chunk in file.chunks():
                destination.write(chunk)
            destination.close()

            #  agrega las rutas para que el archivo se pueda acceder desde el context
            url = "/".join([settings.MEDIA_URL + 'dynaform_uploads', self.object_form.slug, file_name + file_extension])
            self.file_fields[file_field] = dict(filename=file_name + file_extension, url=url,
                                                file=upload_path + '/' + file_name + file_extension)

    def save(self, *args, **kwargs):
        context = self.get_context()
        context.update({'now': datetime.datetime.now()})
        sent_by_mail = self.object_form.send_notification_email(
            recipient_list=self.get_recipient_list(),
            adf_recipient_list=[self.object_form.adf_recipient],
            ctx=context)

        def sanitize(val):
            val = str(val)
            return val.replace('\"', '').replace('\'', '').replace('"', '')

        # GEO IP
        geo_data = self.get_location(self.request)

        data = {'geo_data': geo_data}
        fields_in = ['captcha_0', 'captcha_1', 'captcha', 'csrfmiddlewaretoken',
                     u'recaptcha_response_field', 'utm_source', 'utm_medium', 'utm_campaign']
        for key in self.cleaned_data:
            if key not in fields_in:
                data.update({key: json.dumps(sanitize(self.cleaned_data[key]))})

        dt = TrackingFormularioDinamico(
            site=Site.objects.get_current(),
            sender=self.object_form.name[:200],
            utm_source=self.cleaned_data['utm_source'],
            utm_medium=self.cleaned_data['utm_medium'],
            utm_campaign=self.cleaned_data['utm_campaign'],
            object_form=self.object_form,
            sent_by_mail=sent_by_mail
        )
        dt.data = json.dumps(data)
        dt.save()
        self.dt = dt  # guardo la instancia de TrackingFormularioDinamico para luego poder recuperarla.

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        elif x_real_ip:
            ip = x_real_ip.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_location(self, request):
        try:
            ip = self.get_client_ip(request)
            data = requests.get('http://ip-api.com/json/' + ip, timeout=0.5)

            if data.status_code == requests.status_codes.codes.OK:
                return data.json()
        except:
            pass

        return {}
