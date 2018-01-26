from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from landinator.models.formulario_dinamico import FormularioDinamico

# esto es para que no se pueda borrar el superuser
@receiver(pre_delete, sender=User)
def delete_user(sender, instance, **kwargs):
    if instance.is_superuser:
        raise PermissionDenied


class Landing(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, verbose_name="Landing")
    slug = models.CharField(max_length=100)

    html = models.TextField(verbose_name="HTML del Template")
    form = models.ForeignKey(FormularioDinamico, blank=False, null=False)

    google_code = models.TextField(null=True, blank=True)
    google_conversion_code = models.TextField(null=True, blank=True)
    facebook_code = models.TextField(null=True, blank=True)
    facebook_conversion_code = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/landing/' + self.slug + '/'

    class Meta:
        get_latest_by = 'modified'
        verbose_name = '03 Landing'
        verbose_name_plural = '03 Landings'

