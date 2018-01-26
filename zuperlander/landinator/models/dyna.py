# *-* coding=utf-8 *-*
import logging

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from django.utils import translation
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from landinator.forms.widgets import DYNAFORM_FIELDS, DYNAFORM_WIDGETS

logger = logging.getLogger(__name__)


class MultiSiteBaseManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        """
        Registros para el site actual o sin site
        """
        qs = super(MultiSiteBaseManager, self).get_queryset(*args, **kwargs)
        qs = qs.filter(models.Q(site__id__in=[settings.SITE_ID, ]) | models.Q(site__isnull=True))
        return qs

    def get_for_lang(self, *args, **kwargs):
        """
        Registros para el idioma actual o sin idioma
        """
        qs = self.get_queryset(*args, **kwargs)
        if 'django.middleware.locale.LocaleMiddleware' in getattr(settings, 'MIDDLEWARE_CLASSES', []):
            return qs.filter(models.Q(lang__iexact=translation.get_language()) | models.Q(lang__exact=''))
        else:
            logger.warning('NO get for lang %s', translation.get_language())
        return qs

    def get_for_site_or_none(self, *args, **kwargs):
        """
        Registros para el site actual
        """
        qs = super(MultiSiteBaseManager, self).get_queryset(*args, **kwargs)
        return qs.filter(site__id__in=[settings.SITE_ID, ])


class MultiSiteBaseManagerAdmin(models.Manager):
    pass


class MultiSiteBaseModel(models.Model):
    """
    Base para Multi Site y Lang
    """
    lang = models.CharField(max_length=20, blank=True, choices=settings.LANGUAGES)
    site = models.ManyToManyField(Site, blank=True, related_name="%(app_label)s_%(class)s_related")

    # el primero es el que luego es llamado con _default_manager
    objects_for_admin = MultiSiteBaseManagerAdmin()
    objects = MultiSiteBaseManager()

    class Meta:
        abstract = True


class GenericRelationManager(models.Manager):
    def for_model(self, model):
        """
        Para el modelo en particular y/o su instancia o clase
        """
        ct = ContentType.objects.get_for_model(model)
        qs = self.get_queryset().filter(content_type=ct)
        if isinstance(model, models.Model):
            qs = qs.filter(object_pk=force_text(model._get_pk_val()))
        return qs


class GenericRelationModel(models.Model):
    content_type = models.ForeignKey(ContentType, blank=True, null=True, verbose_name=_('content type'),
                                     related_name="content_type_set_for_%(class)s")
    object_pk = models.PositiveIntegerField(_('object PK'), blank=True, null=True)
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    objects = GenericRelationManager()

    def __str__(self):
        return u"%s" % self.content_object

    class Meta:
        abstract = True


class DynaFormField(GenericRelationModel):
    field_name = models.SlugField(_(u"Identificador del Campo"), max_length=200,
                                  help_text=_(u"nombre del campo solo letras minúsculas, guionbajo y numeros "))
    field_label = models.CharField(_(u"Etiqueta del Campo"), max_length=200, help_text=_(u"nombre visible del campo"))
    field_type = models.CharField(max_length=100, choices=DYNAFORM_FIELDS)
    field_widget = models.CharField(max_length=100, choices=DYNAFORM_WIDGETS, blank=True, null=True)
    field_help = models.CharField(_(u"Texto descripción"), max_length=200, blank=True)

    is_required = models.BooleanField(_(u"Requerido"), default=True)
    is_hidden = models.BooleanField(_(u"Oculto"), default=False)

    default_value = models.CharField(_(u"Valor por defecto"), max_length=200, blank=True, help_text=_(
        u"Se pueden usar variables del contexto {{ object }}, {{ sites }}, etc"))

    choices = models.TextField(_(u"Lista de valores"), blank=True,
                               help_text=_(u"Lista de \"valor\", \"título\" separada por el delimitador y por línea"))
    choices_delimiter = models.CharField(_(u"Delimitador de valores por defecto es |"), max_length=1, blank=True,
                                         default='|')

    ##########################################################################
    # Choices por Modelo
    ##########################################################################
    choices_queryset = models.ForeignKey(ContentType, verbose_name=_(u"Modelo de Datos"), blank=True, null=True)
    choices_queryset_filter = models.CharField(_(u"Filtros"), max_length=200, blank=True)
    choices_queryset_empty_label = models.CharField(_(u"Valor por defecto"), max_length=100, blank=True,
                                                    default="------")
    choices_queryset_label = models.CharField(_(u"Formato"), max_length=100, blank=True, help_text=_(
        u"puede ser cualquier campo del modelo en formato, \"%(nombre)s, %(apellido)s\""))

    choices_related_field = models.ForeignKey('self', blank=True, null=True)

    field_order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['field_order', ]

    def __str__(self):
        return str(self.field_name)

    def choices_queryset_queryset(self, *args, **kwargs):
        """
        Resuelve el modelo y genera el queryset para luego filtrar
        """
        import re
        and_split = re.compile('(?:\s+AND\s+)')
        qs = []
        if self.choices_queryset and self.field_type in \
            ("ModelChoiceField", "ModelMultipleChoiceField"):
            qs = self.choices_queryset.get_all_objects_for_this_type()

            if self.choices_queryset_filter:
                filter_args = dict([f.split('=') for f in self.choices_queryset_filter.split(',')])

                # testing AND y OR
                # and_split.split("name__in=[1,2,4,5, 'AND', ' AND THEN...'] AND id__gt=2")
                # ["name__in=[1,2,4,5, 'AND ']", ' AND ', 'id__gt=2]
                # print and_split.split(self.choices_queryset_filter)
                # filter_args = dict([f.split('=') for f in and_split.split(self.choices_queryset_filter)])

                if filter_args:
                    qs = qs.filter(**filter_args)
        return qs
