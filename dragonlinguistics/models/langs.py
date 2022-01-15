from django.db import models
from django.utils.safestring import mark_safe

class Language(models.Model):
    name = models.CharField('language name', max_length=50)
    code = models.CharField('language code', max_length=5, unique=True)
    blurb = models.TextField(default='')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('langs:view', kwargs={'code': self.code})

    def get_classes(self):
        return mark_safe(f'"lang {self.code}"')
