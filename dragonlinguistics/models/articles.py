from django.db import models

class Folder(models.Model):
    parent = models.ForeignKey('Folder', on_delete=models.CASCADE, null=True, blank=True)
    path = models.TextField()

    @property
    def name(self):
        return self.path.rsplit('/', maxsplit=1)[-1]

    def __str__(self):
        return self.path


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
        return list(filter(None, self.tags.split('\n')))

    def urls(self, action):
        from django.urls import reverse
        kwargs = {'slug': self.slug}
        if self.folder is None:
            namespace = 'articles'
        else:
            parts = list(self.folder.path.split('/'))
            if parts[0] == 'langs':
                kwargs['code'] = parts.pop(1)
                if len(parts) == 1:
                    parts.append('articles')
            namespace = ':'.join(parts)
        return reverse(f'{namespace}:{action}', kwargs=kwargs)

    def get_absolute_url(self):
        return self.urls('view')

    def get_edit_url(self):
        return self.urls('edit')

    def get_delete_url(self):
        return self.urls('delete')
