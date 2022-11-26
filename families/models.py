from collections.abc import Iterator

from django.db import models
from django_hosts.resolvers import reverse

from common.models import BaseModel
from languages.models import Language

class Family(BaseModel):
    name: str = models.CharField(max_length=50)
    type: str = models.CharField(max_length=7, choices=Language.TYPES, default='other')
    blurb: str = models.TextField(default='')

    class Meta:
        ordering = ['name']

    @property
    def root(self) -> 'Clade':
        return self.clades.get(parent=None)

    def __str__(self) -> str:
        return self.name

    def draw_clades(self, use_pipes: bool = True) -> str:
        return self.root.draw(use_pipes=use_pipes)

    def draw_clades_html(self) -> str:
        return self.root.draw_html()

    def parse_clades(self, string: str) -> None:
        Clade.parse(self, string.splitlines())

    def get_host(self) -> str:
        if self.type == 'natlang':
            return 'hist'
        elif self.type == 'conlang':
            return 'conlang'
        else:
            return ''

    def url(self) -> str:
        return reverse('view-family', kwargs={'name': self.name}, host=self.get_host())

    def list_url(self) -> str:
        return reverse('list-families', host=self.get_host())

    def breadcrumbs(self) -> Iterator[tuple[str, str]]:
        yield self.list_url(), 'Families'
        yield self.url(), self.html()


class Clade(BaseModel):
    family: Family = models.ForeignKey(
        Family, related_name='clades', related_query_name='clade', on_delete=models.CASCADE)
    parent: 'Clade' = models.ForeignKey(
        'self', related_name='children', related_query_name='child', on_delete=models.CASCADE, blank=True, null=True)
    language: Language = models.OneToOneField(Language, on_delete=models.SET_NULL, blank=True, null=True)
    name: str = models.CharField(max_length=50)

    def __str__(self) -> str:
        if self.language is not None:
            return str(self.language)
        else:
            return self.name

    def get_classes(self) -> list[str]:
        return ['clade']

    def draw_html(self, prefix: str = '') -> str:
        from django.utils.html import format_html, format_html_join
        from django.utils.safestring import mark_safe
        # nbsp to prevent whitespace collapsing
        stem =   '│   '
        branch = '├── '
        final =  '└── '
        space =  '    '
        if self.language is not None:
            text = format_html('<a href="{}">{}</a>', self.language.url(), self.language.html())
        else:
            text = self.html()
        children: list[Clade] = list(self.children.all())
        if children:
            last = children.pop()
            for child in children:
                text += format_html(
                    '\n<span class="clade-prefix">{}{}</span>{}',
                    prefix, branch, child.draw_html(prefix + stem))
            text += format_html(
                '\n<span class="clade-prefix">{}{}</span>{}',
                prefix, final, last.draw_html(prefix + space))
        return mark_safe(text)

    def draw(self, prefix: str = '', use_pipes: bool = True) -> str:
        if use_pipes:
            stem =   '│   '
            branch = '├── '
            final =  '└── '
            space =  '    '
        else:
            stem = branch = final = space = '  '
        text = str(self)
        children: list[Clade] = list(self.children.all())
        if children:
            last = children.pop()
            for child in children:
                text += f'\n{prefix}{branch}{child.draw(prefix+stem, use_pipes)}'
            text += f'\n{prefix}{final}{last.draw(prefix+space, use_pipes)}'
        return text

    @staticmethod
    def parse(family: Family, lines: list[str], parent: 'Clade | None' = None, prefix: str = '') -> 'Clade | None':
        if lines and lines[0].startswith(prefix):
            name = lines.pop(0).removeprefix(prefix)
            try:
                language = Language.objects.get(type=family.type, name=name)
            except Language.DoesNotExist:
                language = None
            clade = Clade(family=family, parent=parent, language=language, name=name)
            clade.save()
            while True:
                child = Clade.parse(family, lines, parent=clade, prefix=prefix+'  ')
                if child is None:
                    break
            return clade
        else:
            return None
