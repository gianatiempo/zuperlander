from django.db import models

from landinator.models.landing import Landing


class Adjunto(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    file = models.FileField()
    landing = models.ForeignKey(Landing, related_name="adjuntos", verbose_name="landing")

    class Meta:
        verbose_name_plural = "Adjuntos"

    def __str__(self):
        return self.name
