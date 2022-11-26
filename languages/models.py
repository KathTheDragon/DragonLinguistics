from collections.abc import Iterator

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
    type: str = models.CharField(max_length=7, choices=TYPES, default='other')
    name: str = models.CharField('language name', max_length=50)
    code: str = models.CharField('language code', max_length=5, unique=True)
    blurb: str = models.TextField(default='')

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
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

    def get_host(self) -> str:
        if self.type == 'natlang':
            return 'hist'
        elif self.type == 'conlang':
            return 'conlang'
        else:
            return ''

    def url(self) -> str:
        return reverse('view-language', kwargs={'name': self.name}, host=self.get_host())

    def list_url(self) -> str:
        return reverse('list-languages', host=self.get_host())

    def breadcrumbs(self) -> Iterator[tuple[str, str]]:
        yield self.list_url(), 'Languages'
        yield self.url(), self.html()

    def get_classes(self) -> list[str]:
        return ['lang', self.code]

    def get_folders(self) -> dict[str, Folder]:
        return {
            'articles': Folder.objects.get_or_create(path=f'{self.type}s/{self.code}/')[0],
            'grammar': Folder.objects.get_or_create(path=f'{self.type}s/{self.code}/grammar/')[0],
            'lessons': Folder.objects.get_or_create(path=f'{self.type}s/{self.code}/lessons/')[0],
            'texts': Folder.objects.get_or_create(path=f'{self.type}s/{self.code}/texts/')[0],
        }
