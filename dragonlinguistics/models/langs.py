from django.db import models

class Language(models.Model):
    name = models.CharField('language name', max_length=50)
    code = models.CharField('language code', max_length=5, unique=True)
    hasgrammar = models.BooleanField(default=False)
    blurb = models.TextField(default='')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('langs:view', kwargs={'code': self.code})

    class Meta:
        ordering = ['name']
