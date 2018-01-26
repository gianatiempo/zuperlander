from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from landinator.models.dyna import MultiSiteBaseModel


class TemplateFormularioDinamico(MultiSiteBaseModel):
    """
    Templates for dinamic forms for subject, body and form itself
    """
    multisite_unique_together = ('slug',)

    name = models.CharField(_(u"Nombre del template"), max_length=100, help_text=_(u"ej: Subject Contacto"))
    slug = models.SlugField(max_length=100)
    html = models.TextField(_(u"HTML del Template"), help_text=_(u"parsea del contexto, y templatetags"))
    is_plain = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super(TemplateFormularioDinamico, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '02 Template Formulario Dinamico'
        verbose_name_plural = '02 Templates Formularios Dinamicos'
