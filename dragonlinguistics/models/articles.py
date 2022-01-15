from django.db import models

class Folder(models.Model):
    parent = models.ForeignKey('Folder', on_delete=models.CASCADE, null=True, blank=True)
    path = models.TextField()

    @property
    def name(self):
        return self.path.rsplit('/', maxsplit=1)[-1]

    def __str__(self):
        return self.path

    def urls(self, action):
        from django.urls import reverse
        namespace, kwargs = parse_path(self.path)
        return reverse(f'{namespace}:{action}', kwargs=kwargs)

    def get_absolute_url(self):
        return self.urls('list')

    def get_new_url(self):
        return self.urls('new')


class Article(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField()
    title = models.CharField(max_length=255)
    description = models.CharField(blank=True, max_length=255)
    content = models.TextField()
    tags = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return list(filter(None, map(lambda t: t.strip(), self.tags.split(','))))

    def urls(self, action):
        from django.urls import reverse
        kwargs = {'slug': self.slug}
        if self.folder is None:
            namespace, kwargs = parse_path('', kwargs)
        else:
            namespace, kwargs = parse_path(self.folder.path, kwargs)
        return reverse(f'{namespace}:{action}', kwargs=kwargs)

    def get_absolute_url(self):
        return self.urls('view')

    def get_edit_url(self):
        return self.urls('edit')

    def get_delete_url(self):
        return self.urls('delete')


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
