from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django_hosts.resolvers import reverse

from common.models import BaseModel

ASCII_TRANS = str.maketrans({
    'þ': 'th',
    'Þ': 'Th',
})

class Author(BaseModel):
    forenames = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    alphabetise = models.CharField(max_length=255)

    class Meta:
        ordering = ['alphabetise']

    def __str__(self):
        return f'{self.surname}, {self.forenames}'

    @property
    def short(self):
        return f'{self.surname} {self.forenames[0]}'

    def save(self, *args, **kwargs):
        import string
        self.slug = slugify(self.short.translate(ASCII_TRANS))
        self.alphabetise = self.surname.lstrip(string.ascii_lowercase + ' ')
        super().save(*args, **kwargs)

    def url(self):
        return reverse('view-author', kwargs={'name': self.slug}, host='hist')

    def list_url(self):
        return reverse('view-bibliography', host='hist')

    def breadcrumbs(self):
        yield (self.list_url(), 'Bibliography')
        yield (self.url(), self.html())


class Reference(BaseModel):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
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
        index = chr(self.index + ord('a'))
        return f'{self.author.short} ({self.year}{index})'

    def as_html(self):
        html = f'{self.year} - <a href="{self.link}" target="_blank"><em>{escape(self.title)}</em></a>'
        if self.comment:
            html += f' ({escape(self.comment)})'
        return mark_safe(html)

    def url(self):
        return reverse(
            'view-reference',
            kwargs={'name': self.author.slug, 'year': self.year, 'index': self.index},
            host='hist',
        )

    def list_url(self):
        return self.author.url()

    def breadcrumbs(self):
        yield from self.author.breadcrumbs()
        yield (self.url(), self.html())
