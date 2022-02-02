from django.core.exceptions import ValidationError
from django.db import models

class Reference(models.Model):
    author = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    link = models.TextField(blank=True)
    comment = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['author', 'year', 'id']

    def urls(self, action):
        from django.urls import reverse
        titles = [
            title for (title,) in
            self.objects.filter(author=self.author, year=self.year).values_list('titles')
        ]
        return reverse(
            f'references:{action}',
            kwargs={'author': self.author, 'year': self.year, 'index': titles.index(self.title)}
        )

    def get_edit_url(self):
        return self.urls('edit')

    def get_delete_url(self):
        return self.urls('delete')
