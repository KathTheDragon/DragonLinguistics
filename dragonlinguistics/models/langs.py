from django.db import models
from . import base, Folder

class Language(base.Model):
    name = models.CharField('language name', max_length=50)
    code = models.CharField('language code', max_length=5, unique=True)
    blurb = models.TextField(default='')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        Folder.objects.filter(path__startswith=f'langs/{self.code}').delete()
        return super().delete(*args, **kwargs)

    def url(self):
        from django.urls import reverse
        kwargs = {'code': self.code}
        return reverse(f'langs:view', kwargs=kwargs)

    def list_url(self):
        from django.urls import reverse
        return reverse('langs:list')

    def get_classes(self):
        return ['lang', self.code]
