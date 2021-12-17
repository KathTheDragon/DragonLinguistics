from django.db import models

class Folder(models.Model):
    parent = models.ForeignKey('Folder', on_delete=models.CASCADE, null=True)
    path = models.TextField()

    @property
    def name(self):
        return self.path.rsplit('/', maxsplit=1)[-1]

    def __str__(self):
        return self.path


class Article(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
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

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('articles:view', kwargs={'slug': self.slug})
