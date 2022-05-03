from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import slugify

class Folder(models.Model):
    path = models.TextField(blank=True)

    @property
    def name(self):
        return self.path.rsplit('/', maxsplit=1)[-1]

    def __str__(self):
        return self.path

    def get_absolute_url(self):
        from django.urls import reverse
        namespace, kwargs = parse_path(self.path)
        return reverse(f'{namespace}:list', kwargs=kwargs)


class Article(models.Model):
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

    def html(self):
        from django.utils.html import format_html
        return format_html(
            '<span class={}>{}</span>',
            self.get_classes(),
            self,
        )

    @property
    def tag_list(self):
        return list(filter(None, map(lambda t: t.strip(), self.tags.split(','))))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        kwargs = {'slug': self.slug}
        if self.folder is None:
            namespace, kwargs = parse_path('', kwargs)
        else:
            namespace, kwargs = parse_path(self.folder.path, kwargs)
        return reverse(f'{namespace}:view', kwargs=kwargs)

    def get_classes(self):
        return mark_safe(f'"article"')


def parse_path(path, kwargs=None):
    if kwargs is None:
        kwargs = {}
    parts = path.split('/')
    if parts[0] == 'langs':
        kwargs['code'] = parts[1]
        if len(parts) == 2:
            kwargs['type'] = 'articles'
        else:
            kwargs['type'] = parts[2]
        namespace = 'langs:articles'
    else:
        namespace = 'articles'
    return namespace, kwargs
