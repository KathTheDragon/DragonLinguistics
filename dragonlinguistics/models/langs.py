from django.db import models
from django.utils.safestring import mark_safe
from . import Folder

class Language(models.Model):
    name = models.CharField('language name', max_length=50)
    code = models.CharField('language code', max_length=5, unique=True)
    blurb = models.TextField(default='')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def html(self):
        from django.utils.html import format_html
        return format_html(
            '<span class={}>{}</span>',
            self.get_classes(),
            self,
        )

    def delete(self, *args, **kwargs):
        Folder.objects.filter(path__startswith=f'langs/{self.code}').delete()
        return super().delete(*args, **kwargs)

    def urls(self, action):
        from django.urls import reverse
        kwargs = {'code': self.code}
        return reverse(f'langs:{action}', kwargs=kwargs)

    def get_absolute_url(self):
        return self.urls('view')

    def get_edit_url(self):
        return self.urls('edit')

    def get_delete_url(self):
        return self.urls('delete')

    def get_classes(self):
        return mark_safe(f'"lang {self.code}"')
