import os

from django.contrib.admin.widgets import AdminFileWidget
from django.db import models
from django.utils.safestring import mark_safe

from config.settings.common import MEDIA_URL
from landinator.models.landing import Landing


class Imagen(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    image = models.ImageField()
    landing = models.ForeignKey(Landing, related_name="imagenes", verbose_name="landing")

    class Meta:
        verbose_name_plural = "Imagenes"

    def __str__(self):
        return self.name

    def image_tag(self):
        return mark_safe('<img src="%s%s" style="max-height: 150px;"/>' % (MEDIA_URL, os.path.basename(self.imagen.name)))

    image_tag.short_description = 'Imagen'


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            output.append(u'<img src="%s" style="max-height: 70px; float: right;"/>' % image_url)
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
