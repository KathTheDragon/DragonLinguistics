from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from . import base

class Reference(base.Model):
    author = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    link = models.URLField(max_length=255, blank=True)
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

    def __str__(self):
        author = self.author.split(',', maxsplit=1)[0]
        index = chr(self.index + ord('a'))
        return f'{author} ({self.year}{index})'

    def as_html(self):
        html = f'{self.year} - <a href="{self.link}" target="_blank"><em>{escape(self.title)}</em></a>'
        if self.comment:
            html += f' ({escape(self.comment)})'
        return mark_safe(html)

    def url(self):
        from django.urls import reverse

        return reverse(
            f'references:view',
            kwargs={'author': self.author, 'year': self.year, 'index': self.index}
        )
