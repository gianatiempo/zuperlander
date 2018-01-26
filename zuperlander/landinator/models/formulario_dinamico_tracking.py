from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _


class TrackingFormularioDinamico(models.Model):
    pub_date = models.DateTimeField(auto_now=True, verbose_name=_(u"Fecha de creación"))
    site = models.ForeignKey(Site)
    lang = models.CharField(max_length=20, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE.lower())
    sender = models.CharField(max_length=200)
    utm_source = models.CharField(max_length=200, blank=True, null=True)
    utm_medium = models.CharField(max_length=200, blank=True, null=True)
    utm_campaign = models.CharField(max_length=200, blank=True, null=True)
    data = JSONField()
    object_form = models.ForeignKey('FormularioDinamico', blank=True, null=True)
    sent_by_mail = models.BooleanField(default=False)

    def __str__(self, *args, **kwargs):
        return u"%s %s" % (self.pub_date, self.sender)

    def save(self, *args, **kwargs):
        super(TrackingFormularioDinamico, self).save(*args, **kwargs)

    def get_data(self):
        if isinstance(self.data, dict):
            return self.data
        elif isinstance(self.data, (list, tuple)):
            return dict(zip(range(len(self.data)), self.data))


class TrackingEnviadoManager(models.Manager):
    def get_queryset(self):
        return super(TrackingEnviadoManager, self).get_queryset().filter(sent_by_mail=True)


class TrackingNoEnviadoManager(models.Manager):
    def get_queryset(self):
        return super(TrackingNoEnviadoManager, self).get_queryset().filter(sent_by_mail=False)


class TrackingEnviado(TrackingFormularioDinamico):
    class Meta:
        proxy = True
        verbose_name = '04 Tracking Formulario Enviado Por Email'
        verbose_name_plural = '04 Tracking Formularios Enviados Por Email'

    objects = TrackingEnviadoManager()


class TrackingNoEnviado(TrackingFormularioDinamico):
    class Meta:
        proxy = True
        verbose_name = '05 Tracking Formulario No Enviado Por Email'
        verbose_name_plural = '05 Tracking Formularios No Enviados Por Email'

    objects = TrackingNoEnviadoManager()
