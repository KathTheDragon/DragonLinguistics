from django.db import models
from django_hosts.resolvers import reverse

from common.models import BaseModel
from articles.models import Folder

class Language(BaseModel):
    TYPES = [
        ('natlang', 'Natlang'),
        ('conlang', 'Conlang'),
        ('other',   'Other'),
    ]
    type = models.CharField(max_length=7, choices=TYPES, default='other')
    name = models.CharField('language name', max_length=50)
    code = models.CharField('language code', max_length=5, unique=True)
    blurb = models.TextField(default='')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        from dictionaries.models import Dictionary
        folders = Language.objects.get(pk=self.pk).get_folders()
        prefix = folders['articles'].path
        for folder in folders.values():
            folder.path = folder.path.replace(prefix, f'{self.type}s/{self.code}/')
            folder.save()
        super().save(*args, **kwargs)
        Dictionary.objects.get_or_create(language=self)
        self.get_folders()

    def delete(self, *args, **kwargs):
        for folder in self.get_folders().values():
            folder.delete()
        return super().delete(*args, **kwargs)

    def get_host(self):
        if self.type == 'natlang':
            return 'hist'
        elif self.type == 'conlang':
            return 'conlang'
        else:
            return ''

    def url(self):
        return reverse('view-language', kwargs={'name': self.name}, host=self.get_host())

    def list_url(self):
        return reverse('list-languages', host=self.get_host())

    def breadcrumbs(self):
        yield (self.list_url(), 'Languages')
        yield (self.url(), self.html())

    def get_classes(self):
        return ['lang', self.code]

    def get_folders(self):
        return {
            'articles': Folder.objects.get_or_create(path=f'{self.type}s/{self.code}/')[0],
            'grammar': Folder.objects.get_or_create(path=f'{self.type}s/{self.code}/grammar/')[0],
            'lessons': Folder.objects.get_or_create(path=f'{self.type}s/{self.code}/lessons/')[0],
            'texts': Folder.objects.get_or_create(path=f'{self.type}s/{self.code}/texts/')[0],
        }
