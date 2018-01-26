import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template import Template
from django.template.defaultfilters import escape, safe
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from landinator.models.dyna import MultiSiteBaseModel, DynaFormField
from landinator.models.formulario_dinamico_template import TemplateFormularioDinamico

log = logging.getLogger(__name__)


class FormularioDinamico(MultiSiteBaseModel):
    """
    Create dinamic forms from database
    """
    multisite_unique_together = ('slug',)

    name = models.CharField(_(u"Nombre del form"), max_length=100)
    slug = models.SlugField(max_length=100)
    is_active = models.BooleanField(_(u"Es activo"), default=True, help_text=_(u"activa para usar en el frontend"))

    form_title = models.CharField(_(u"Título del form"), max_length=200)
    form_template = models.ForeignKey(TemplateFormularioDinamico, related_name="dynaform_form_template_related",
                                      blank=True, null=True)

    ##########################################################################
    # Limite de envios al guardar
    ##########################################################################
    limite_envios = models.IntegerField(default=-1, help_text="Ingrese la cantidad de formularios completados que se enviaran por mail o -1 para no limitarlo")
    envios = models.IntegerField(default=0)

    ##########################################################################
    # Enviar mail al guardar
    ##########################################################################
    send_email = models.BooleanField(_("Enviar mail"), default=True)
    from_email = models.CharField(max_length=100, default=settings.DEFAULT_FROM_EMAIL, blank=True)
    recipient_list = models.TextField(_(u"Lista de destinatarios"), blank=True,
                                      help_text=_(u"ej: lista separada por líneas y coma.<br>Juan Pérez, juanperez@dominio.com<br>Maria Gomez, mariagomez@dominio.com"))

    subject_template = models.ForeignKey(TemplateFormularioDinamico, blank=True, null=True, related_name="dynaform_subject_template_related")
    body_template = models.ForeignKey(TemplateFormularioDinamico, blank=True, null=True, related_name="dynaform_body_template_related")
    error_class = models.CharField(_(u"Clase CSS para error"), max_length=40, default="error")
    required_css_class = models.CharField(_(u"Clase CSS para requerido"), max_length=40, default="required")

    ##########################################################################
    # Enviar mail ADF al guardar
    ##########################################################################
    adf_send_email = models.BooleanField(_("Enviar mail ADF"), default=False)
    adf_from_email = models.CharField(max_length=100, default=settings.DEFAULT_FROM_EMAIL, blank=True)
    adf_recipient = models.CharField(_(u"Email CRM"), max_length=100, blank=True, help_text=_(u"ej: CRM@dominio.com"))
    adf_subject_template = models.ForeignKey(TemplateFormularioDinamico, blank=True, null=True, related_name="dynaform_adf_subject_template_related")
    adf_body_template = models.ForeignKey(TemplateFormularioDinamico, blank=True, null=True, related_name="dynaform_adf_body_template_related")

    ##########################################################################
    # nuevo autorespondedor
    ##########################################################################
    autorespond = models.BooleanField(_(u"Autoresponder"), default=False)
    autorespond_subject_template = models.ForeignKey(TemplateFormularioDinamico, blank=True, null=True,
                                                     related_name="dynaform_autorespond_subject_template_related")
    autorespond_body_template = models.ForeignKey(TemplateFormularioDinamico, blank=True, null=True,
                                                  related_name="dynaform_autorespond_body_template_related")
    autorespond_email_field = models.CharField(_("Campo de email"), default='email', max_length=40)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super(FormularioDinamico, self).save(*args, **kwargs)

    def get_fields(self):
        return DynaFormField.objects.for_model(self)

    @models.permalink
    def get_absolute_url(self):
        return ('dynaform_action', (), {'slug': self.slug, 'pk': self.pk})

    def clone(self):
        """
        Hace un clon de la instania actual

        """

        # recrea la instancia del form
        form_clone = FormularioDinamico(
            lang=self.lang,
            name="clon de %s" % self.name,
            is_active=self.is_active,
            form_title=self.form_title,
            form_template=self.form_template,
            send_email=self.send_email,
            from_email=self.from_email,
            recipient_list=self.recipient_list,
            subject_template=self.subject_template,
            body_template=self.body_template,
            error_class=self.error_class,
            required_css_class=self.required_css_class,
            autorespond=self.autorespond,
            autorespond_subject_template=self.autorespond_subject_template,
            autorespond_body_template=self.autorespond_body_template,
            autorespond_email_field=self.autorespond_email_field
        )

        form_clone.save()

        content_type = ContentType.objects.get_for_model(form_clone)

        # recrea todos los fields
        for field in self.get_fields():
            field_clone = DynaFormField(
                content_type=content_type,
                object_pk=form_clone.pk,
                field_name=field.field_name,
                field_label=field.field_label,
                field_type=field.field_type,
                field_widget=field.field_widget,
                field_help=field.field_help,
                is_required=field.is_required,
                is_hidden=field.is_hidden,
                default_value=field.default_value,
                choices=field.choices,
                choices_delimiter=field.choices_delimiter,
                choices_queryset=field.choices_queryset,
                choices_queryset_filter=field.choices_queryset_filter,
                choices_queryset_empty_label=field.choices_queryset_empty_label,
                choices_queryset_label=field.choices_queryset_label,
                choices_related_field=field.choices_related_field,
                field_order=field.field_order
            )

            field_clone.save()

    class Meta:
        verbose_name = '01 Formulario Dinamico'
        verbose_name_plural = '01 Formularios Dinamicos'

    def send_notification_email(self, ctx, recipient_list=None, adf_recipient_list=None, ignore_limit=False):
        sent_by_mail = False
        if (self.limite_envios > 0 and self.envios < self.limite_envios) or self.limite_envios == -1 or ignore_limit:
            if self.send_email:
                subject_template = Template(self.subject_template.html)
                body_template = Template(self.body_template.html)
                subject = subject_template.render(ctx)
                body = body_template.render(ctx)
                to_list = recipient_list

                if self.body_template.is_plain:
                    msg = EmailMultiAlternatives(subject, safe(body), self.from_email, to_list)
                else:
                    msg = EmailMultiAlternatives(subject, escape(body), self.from_email, to_list)
                    msg.attach_alternative(body, "text/html")

                msg.send()
                log.info("Email sent")

            if self.adf_send_email:
                adf_subject_template = Template(self.adf_subject_template.html)
                adf_body_template = Template(self.adf_body_template.html)
                adf_subject = adf_subject_template.render(ctx)
                adf_body = adf_body_template.render(ctx)
                to_list = adf_recipient_list

                if self.adf_body_template.is_plain:
                    adf_msg = EmailMultiAlternatives(adf_subject, safe(adf_body), self.adf_from_email, to_list)
                else:
                    adf_msg = EmailMultiAlternatives(adf_subject, escape(adf_body), self.adf_from_email, to_list)
                    adf_msg.attach_alternative(adf_body, "text/html")

                adf_msg.send()
                log.info("ADF Email sent")

            if self.send_email or self.adf_send_email:
                sent_by_mail = True
                self.envios += 1
                self.save()

        if self.autorespond:
            subject_template = Template(self.autorespond_subject_template.html)
            body_template = Template(self.autorespond_body_template.html)
            subject = subject_template.render(ctx)
            body = body_template.render(ctx)
            email_to = self.cleaned_data[self.autorespond_email_field]

            if self.autorespond_body_template.is_plain:
                msg = EmailMultiAlternatives(subject, safe(body), self.from_email, [email_to, ])
            else:
                msg = EmailMultiAlternatives(subject, escape(body), self.from_email, [email_to, ])
            msg.send()
            log.info("Email autorespond sent")

        return sent_by_mail


class FacebookAdCode(models.Model):
    formulario = models.ForeignKey(FormularioDinamico, null=True, blank=True, on_delete=models.CASCADE)
    code = models.CharField(_(u"Identificador de Anuncio"), max_length=30, help_text=_(u"codigo numerico del anuncio creado en facebook"))

    def __str__(self):
        return str(self.code)


class FacebookFanPage(models.Model):
    nombre = models.CharField(_(u"Nombre de la Fan Page"), max_length=200)
    fan_page_id = models.CharField(_(u"ID de la Fan Page"), max_length=200)
    token = models.CharField(_(u"Token de la Fan Page"), max_length=500)

    def __str__(self):
        return str(self.nombre)
