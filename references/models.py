from collections.abc import Iterator

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import escape
from django.utils.safestring import mark_safe, SafeString
from django.utils.text import slugify
from django_hosts.resolvers import reverse

from common.models import BaseModel

ASCII_TRANS = str.maketrans({
    'þ': 'th',
    'Þ': 'Th',
})

class Author(BaseModel):
    forenames: str = models.CharField(max_length=255)
    surname: str = models.CharField(max_length=255)
    slug: str = models.CharField(max_length=255)
    alphabetise: str = models.CharField(max_length=255)

    class Meta:
        ordering = ['alphabetise']

    def __str__(self) -> str:
        return f'{self.surname}, {self.forenames}'

    @property
    def short(self) -> str:
        return f'{self.surname} {self.forenames[0]}'

    def save(self, *args, **kwargs) -> None:
        import string
        self.slug = slugify(self.short.translate(ASCII_TRANS))
        self.alphabetise = self.surname.lstrip(string.ascii_lowercase + ' ')
        super().save(*args, **kwargs)

    def url(self) -> str:
        return reverse('view-author', kwargs={'name': self.slug}, host='hist')

    def list_url(self) -> str:
        return reverse('view-bibliography', host='hist')

    def breadcrumbs(self):
        yield self.list_url(), 'Bibliography'
        yield self.url(), self.html()


class Reference(BaseModel):
    author: Author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    year: int = models.PositiveSmallIntegerField()
    title: str = models.CharField(max_length=255)
    link: str = models.URLField(max_length=255, blank=True)
    comment: str = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['author', 'year', 'id']

    @property
    def index(self) -> int:
        titles = [
            title for (title,) in
            Reference.objects.filter(author=self.author, year=self.year).values_list('title')
        ]
        return titles.index(self.title)

    def __str__(self) -> str:
        index = chr(self.index + ord('a'))
        return f'{self.author.short} ({self.year}{index})'

    def as_html(self) -> SafeString:
        html = f'{self.year} - <a href="{self.link}" target="_blank"><em>{escape(self.title)}</em></a>'
        if self.comment:
            html += f' ({escape(self.comment)})'
        return mark_safe(html)

    def url(self) -> str:
        return reverse(
            'view-reference',
            kwargs={'name': self.author.slug, 'year': self.year, 'index': self.index},
            host='hist',
        )

    def list_url(self) -> str:
        return self.author.url()

    def breadcrumbs(self) -> Iterator[tuple[str, str]]:
        yield from self.author.breadcrumbs()
        yield self.url(), self.html()
