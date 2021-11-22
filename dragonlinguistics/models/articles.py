from django.db import models

class Folder(models.Model):
    parent = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True)
    path = models.TextField()

    @property
    def name(self):
        return self.path.rsplit('/', maxsplit=1)[-1]


class Article(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    slug = models.SlugField()
    title = models.CharField(length=255)
    description = models.CharField(length=255)
    content = models.TextField()
    tags = models.ManyToManyField('Tag')
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('articles:view', kwargs={'slug': self.slug})


class Tag(models.Model):
    text = models.CharField(max_length=50)
