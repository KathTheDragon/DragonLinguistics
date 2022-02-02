from django.core.exceptions import ValidationError
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import slugify

class Reference(models.Model):
    author = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    link = models.TextField(blank=True)
    comment = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['author', 'year', 'id']

    @property
    def index(self):
        titles = [
            title for (title,) in
            Reference.objects.filter(author=self.author, year=self.year).values_list('title')
        ]
        return titles.index(self.title)

    def long_str(self):
        html = f'{self.year} - <a href="{self.link}" target="_blank"><em>{self.title}</em></a>'
        if self.comment:
            html += f' ({self.comment})'
        return mark_safe(html)

    def short_str(self):
        author = self.author.split(',', maxsplit=1)[0]
        index = chr(self.index + ord('a'))
        return f'{author} ({self.year}{index})'

    def urls(self, action):
        from django.urls import reverse

        return reverse(
            f'references:{action}',
            kwargs={'author': self.author, 'year': self.year, 'index': self.index}
        )

    def get_edit_url(self):
        return self.urls('edit')

    def get_delete_url(self):
        return self.urls('delete')
