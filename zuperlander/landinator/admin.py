import datetime
import json

import nested_admin
from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.http import HttpResponse
from django.template import Context
from django.utils.safestring import mark_safe

from landinator.models.adjunto import Adjunto
from landinator.models.dyna import DynaFormField
from landinator.models.formulario_dinamico import FormularioDinamico, FacebookAdCode
from landinator.models.formulario_dinamico_template import TemplateFormularioDinamico
from landinator.models.formulario_dinamico_tracking import TrackingEnviado, TrackingNoEnviado, \
    TrackingFormularioDinamico
from landinator.models.imagen import Imagen, AdminImageWidget
from landinator.models.landing import Landing


class ImagenInLine(nested_admin.NestedTabularInline):
    fields = ('name', 'image')
    model = Imagen
    extra = 0

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'image':
            request = kwargs.pop("request", None)
            kwargs['widget'] = AdminImageWidget
            return db_field.formfield(**kwargs)
        return super(ImagenInLine, self).formfield_for_dbfield(db_field, **kwargs)


class AdjuntoInLine(nested_admin.NestedTabularInline):
    fields = ('name', 'file')
    model = Adjunto
    extra = 0


class LandingAdmin(nested_admin.NestedModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(LandingAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'html':
            attrs = formfield.widget.attrs
            attrs.update({'rows': 100, 'style': 'color:green;width: calc(100% - 185px);height: 400px;'})
            formfield.widget = forms.Textarea(attrs=attrs)
        return formfield

    view_on_site = True
    list_display = ('name', 'slug', 'created', 'view_link')
    list_filter = ('created', )
    search_fields = ('name', 'title')
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {'fields': ('name', 'slug'), }),
        ('Template', {
            'classes': ('collapse', 'collapsed'),
            'fields': ('html', 'form'),
         }),
        ('Metricas Google', {
             'classes': ('collapse', 'collapsed'),
             'fields': (('google_code', 'google_conversion_code'), ),
         }),
        ('Metricas Facebook', {
            'classes': ('collapse', 'collapsed'),
            'fields': (('facebook_code', 'facebook_conversion_code'), ),
        }),
    )

    inlines = [AdjuntoInLine, ImagenInLine]

    def view_link(self, obj):
        url = obj.get_absolute_url()
        msg = 'Ver'
        return mark_safe('<a href="{0}">{1}</a>'.format(url, msg))

    view_link.allow_tags = True
    view_link.short_description = "Ver"


class DynaFormFieldInline(GenericStackedInline):
    model = DynaFormField
    ct_field = 'content_type'
    ct_fk_field = 'object_pk'
    extra = 1
    fieldsets = (
        (None, {
            'fields': (
                ('field_name', 'field_label'),
                ('field_type', 'field_widget'),
                ('field_help', 'is_required', 'is_hidden'),
                ('default_value', ),
                'field_order',
            ),
        }),

        ('Choices Manual', {
            'fields': (
                ('choices_delimiter', 'choices'),
            ),
            'classes': ('collapse',)
        }),

        ('Choices Modelo de Datos', {
            'fields': (
                ('choices_queryset', 'choices_queryset_empty_label',),
                ('choices_queryset_filter', 'choices_queryset_label'),
                ('choices_related_field',),
            ),
            'classes': ('collapse',)
        }),
    )


class FacebookCodeInline(admin.TabularInline):
    model = FacebookAdCode
    extra = 1


class FormularioDinamicoAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'id')
    inlines = [FacebookCodeInline, DynaFormFieldInline]
    prepopulated_fields = {'slug': ('name',), 'form_title': ('name',)}
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'slug',),
                ('error_class', 'required_css_class'),
                ('form_title', 'form_template'),
                ('is_active',),
                ('limite_envios', 'envios'),
            )
        }),

        ('Advanced setting', {
            'fields': (
                'lang',
                'site',
            ),
            'classes': ('collapse',),
        }),

        ('Send Email', {
            'fields': (
                ('send_email', 'from_email'),
                'recipient_list',
                ('subject_template', 'body_template',),
            ),
            'classes': ('collapse',)
        }),

        ('Send ADF Email', {
            'fields': (
                ('adf_send_email', 'adf_from_email'),
                'adf_recipient',
                ('adf_subject_template', 'adf_body_template',),
            ),
            'classes': ('collapse',)
        }),

        ('Autorespond Email', {
            'fields': (
                ('autorespond', 'autorespond_email_field'),
                ('autorespond_subject_template', 'autorespond_body_template',),
            ),
            'classes': ('collapse',)
        }),
    )
    actions = ['clone_form', ]

    class Meta:
        model = FormularioDinamico

    def clone_form(self, request, queryset):
        for obj in queryset:
            obj.clone()

    clone_form.short_description = "Clonar formulario"


class TemplateFormularioDinamicoAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(TemplateFormularioDinamicoAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'html':
            attrs = formfield.widget.attrs
            attrs.update({'rows': 100, 'style': 'color:green;width: calc(100% - 185px);height: 400px;'})
            formfield.widget = forms.Textarea(attrs=attrs)
        return formfield

    class Meta:
        model = TemplateFormularioDinamico


def export_xls(modeladmin, request, queryset):
    import io
    from xlsxwriter.workbook import Workbook

    output = io.BytesIO()

    wb = Workbook(output, {'in_memory': True})
    ws = wb.add_worksheet()
    date_format = wb.add_format({'num_format': 'mmm d yyyy hh:mm AM/PM'})

    columns = [u"Fecha", ]
    ws.write(0, 0, "Fecha")

    row_num = 0
    col_num = 1
    for enviado in queryset:
        fields = enviado.object_form.get_fields()  # cargo campos del form
        for field in fields:
            col_name = str(field.field_name)
            if col_name not in columns:
                columns.append(col_name)
                ws.write(0, col_num, col_name[:1].upper() + col_name[1:])
                col_num += 1

        enviado_json = json.loads(enviado.data)
        keys = sorted(enviado_json.keys())  # cargo campos adicionales que estan en el json
        for field in keys:
            if field.startswith('geo') and field != "geo_data":
                columns.append(field)
                ws.write(0, col_num, field[:1].upper() + field[1:])
                col_num += 1

        row_num += 1
        for col_num in range(len(columns)):
            if col_num == 0:
                date = enviado.pub_date - datetime.timedelta(hours=3)
                ws.write(row_num, col_num, date.strftime("%Y-%m-%d %H:%M:%S"), date_format)
            else:
                campo_buscado = columns[col_num]
                ws.write(row_num, col_num, enviado_json[campo_buscado])

    wb.close()
    output.seek(0)

    r = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    r['Content-Disposition'] = "attachment; filename=tracking.xlsx"
    return r
export_xls.short_description = u"Exportar Excel"


class TrackingEnviadoAdmin(nested_admin.NestedModelAdmin):
    actions = [export_xls]
    list_display = ('pub_date', 'sender', 'utm_source', 'utm_medium', 'utm_campaign')
    list_filter = ('pub_date', 'sender', 'utm_source', 'utm_medium', 'utm_campaign')


def send_email(self, request, queryset):
    from django.contrib.admin import helpers
    from django.template.response import TemplateResponse

    if request.POST.get('post'):
        adf_emails = []
        txt_emails = []
        idx = 0
        go = True
        while go:
            email = request.POST.get('emails['+str(idx)+']')
            adf = request.POST.get('adf['+str(idx)+']')

            if email: # tengo un mail
                if adf: # el email que tengo es adf
                    adf_emails.append(email)
                else:
                    txt_emails.append(email)

                idx += 1
            else:
                go = False

        trackings_to_send = request.POST.getlist('_selected_action')
        trackings = TrackingFormularioDinamico.objects.filter(id__in=trackings_to_send)
        for tracking in trackings:
            formulario_dinamico = tracking.object_form
            dt = json.loads(tracking.data)
            for key in dt.keys():
                val = dt[key]
                val = str(val).strip('"')
                dt[key] = val

            cont = Context(dt)
            cont.update({'now': datetime.datetime.now()})
            formulario_dinamico.send_notification_email(ctx=cont, recipient_list=txt_emails, adf_recipient_list=adf_emails, ignore_limit=True)
            tracking.sent_by_mail = True
            tracking.save()

        self.message_user(request, "Mail sent successfully.")
    else:
        context = {
            'title': "Are you sure?",
            'queryset': queryset,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        }
        return TemplateResponse(request, 'send_email.html', context)
send_email.short_description = u"Enviar por Email"


class TrackingNoEnviadoAdmin(nested_admin.NestedModelAdmin):
    actions = [send_email]
    list_display = ('pub_date', 'sender', 'utm_source', 'utm_medium', 'utm_campaign')
    list_filter = ('pub_date', 'sender', 'utm_source', 'utm_medium', 'utm_campaign')

    def get_actions(self, request):
        actions = super(TrackingNoEnviadoAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions


admin.site.register(Landing, LandingAdmin)
admin.site.register(FormularioDinamico, FormularioDinamicoAdmin)
admin.site.register(TemplateFormularioDinamico, TemplateFormularioDinamicoAdmin)
admin.site.register(TrackingEnviado, TrackingEnviadoAdmin)
admin.site.register(TrackingNoEnviado, TrackingNoEnviadoAdmin)
