from django.db import models
from django.utils.text import slugify
from django_hosts.resolvers import reverse

from common.models import BaseModel

'''
{conlangs, natlangs}/
    <code>/
        grammar
        lessons
        texts
'''

class Folder(BaseModel):
    path = models.TextField(blank=True)

    @property
    def name(self):
        return self.path.rsplit('/', maxsplit=1)[-1]

    def __str__(self):
        return self.path

    def url(self):
        host, kind, kwargs = parse_path(self.path)
        return reverse(f'list-{kind}', kwargs=kwargs, host=host)


class Article(BaseModel):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    slug = models.SlugField()
    title = models.CharField(max_length=255)
    description = models.CharField(blank=True, max_length=255)
    number = models.CharField(blank=True, max_length=5)  # Used for section numbering
    content = models.TextField()
    tags = models.TextField(blank=True)
    created = models.DateTimeField()
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.title

    def get_string(self):
        if self.folder.path == 'natlangs/':
            return f'{super().get_string()} ({self.created.year})'
        else:
            return super().get_string()

    @property
    def tag_list(self):
        return list(filter(None, map(lambda t: t.strip(), self.tags.split(','))))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def url(self):
        host, kind, kwargs = parse_path(self.folder.path, {'slug': self.slug})
        return reverse(f'view-{kind.removesuffix("s")}', kwargs=kwargs, host=host)

    def list_url(self):
        return self.folder.url()

    def get_classes(self):
        return ['article']

    @property
    def citeable(self):
        return self.folder.path == 'natlangs/'


def parse_path(path, kwargs=None):
    from languages.models import Language
    if kwargs is None:
        kwargs = {}
    parts = path.strip('/').split('/')
    host = {
        'conlangs': 'conlang',
        'natlangs': 'hist',
    }.get(parts[0], '')
    if len(parts) == 1:
        kind = 'articles'
    else:
        kwargs['name'] = Language.objects.get(code=parts[1]).name
        if len(parts) == 2:
            kind = 'lang-articles'
        else:
            kind = parts[2]
    return host, kind, kwargs
