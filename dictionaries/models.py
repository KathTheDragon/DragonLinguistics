import re

from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_hosts.resolvers import reverse

from common.models import BaseModel
from languages.models import Language

def parse_class_list(lines, index=0, indent=''):
    options = []
    groups = []
    while index < len(lines):
        line = lines[index]
        _indent = re.match(r'\s*', line)[0]
        if _indent == line:
            pass
        elif _indent == indent:
            line = line.strip()
            if line.endswith(':'):
                line = line.removesuffix(':')
                groups.append(parse_class(line))
                _indent = re.match(r'\s*', lines[index+1])[0]
                if not _indent.startswith(indent):
                    raise ValueError(f'indent must increase after a group line (line {index+1})')
                _options, index = parse_class_list(lines, index+1, _indent)
                if not indent:
                    options.extend([(name, merge_group(_options, code)) for code, name in groups])
                else:
                    options.extend([option for group in groups for option in merge_group(_options, *group)])
                groups = []
                continue
            elif line.endswith(';'):
                line = line.removesuffix(';')
                groups.append(parse_class(line))
            else:
                if groups:
                    raise ValueError(f'incomplete group definition (line {index})')
                options.append(parse_class(line))
        elif indent.startswith(_indent):  # Dedent
            break
        elif _indent.startswith(indent):  # Indent
            raise ValueError(f'unexpected indentation (line {index})')
        else:
            raise ValueError(f'invalid indentation (line {index})')
        index += 1

    if groups:
        raise ValueError(f'incomplete group definition (line {index})')
    return options, index


def parse_class(line):
    parts = line.split(',')
    if len(parts) == 1:
        code = name = parts[0]
    else:
        code, name = parts[:2]
    return code.strip(), name.strip()


def merge_group(options, code, name=''):
    return [(f'{_code} {code}', f'{_name} {name}' if name else _name) for _code, _name in options]


DERIVATIONS = {
    'LOAN': ('loan', 'from'),
    'FROM': ('inherited', 'from'),
}

class Dictionary(BaseModel):
    language = models.OneToOneField(Language, on_delete=models.CASCADE)
    classes = models.TextField('lexical classes', blank=True)
    order = models.TextField('alphabetical order', blank=True)  # Not using yet
    derivations = models.TextField(blank=True)
    # words

    def __str__(self):
        return f'{self.language} Dictionary'

    def get_class_options(self):
        return parse_class_list(self.classes.splitlines())[0]

    def get_class_dict(self):
        class_dict = {}
        for option in self.get_class_options():
            if isinstance(option[1], str):
                class_dict[option[0]] = option[1]
            else:
                group, options = option
                for key, value in options:
                    class_dict[key] = f'{group} ({value})'
        return class_dict

    def get_class_list(self):
        return list(self.get_class_dict())

    def get_derivation_dict(self):
        return DERIVATIONS | {
            code: (kind, 'of')
            for derivation in self.derivations.splitlines()
            for code, kind in map(str.strip, derivation.split(','))}

    def get_derivation_options(self):
        return [(code, kind) for code, (kind, _) in self.get_derivation_dict().items()]

    def url(self):
        return reverse('view-dictionary', kwargs={'name': self.language.name}, host=self.language.get_host())

    def breadcrumbs(self):
        yield from self.language.breadcrumbs()
        yield (self.url(), 'Dictionary')


class Word(BaseModel):
    dictionary = models.ForeignKey(Dictionary, related_name='words', related_query_name='word', on_delete=models.CASCADE, null=True)
    lemma = models.CharField(max_length=50)
    isunattested = models.BooleanField(default=False)
    gloss = models.CharField(max_length=50, blank=True)
    # etymology
    references = models.TextField(blank=True)
    # variants

    class Meta:
        ordering = ['lemma', 'id']

    def get_homonym(self):
        ids = [
            id for (id,) in
            Word.objects.filter(dictionary=self.dictionary, lemma=self.lemma).values_list('id')
        ]
        if ids == [self.id]:
            return 0
        else:
            return ids.index(self.id) + 1

    def __str__(self):
        return self.citation()

    def citation(self):
        citation = {
            'r': '√{}',
            's': '{}-',
            'pf': '{}-',
            'if': '<{}>',
            'sf': '-{}',
            'pc': '{}=',
            'ec': '={}',
        }.get(self.get_type(), '{}').format(self.lemma)
        if self.isunattested:
            citation = '*' + citation
        return citation

    def url(self):
        homonym = self.get_homonym()
        if homonym:
            lemma = f'{self.lemma}-{homonym}'
        else:
            lemma = self.lemma
        return reverse(
            'view-word',
            kwargs={'name': self.dictionary.language.name, 'lemma': lemma},
            host=self.dictionary.language.get_host(),
        )

    def list_url(self):
        return self.dictionary.url()

    def breadcrumbs(self):
        yield from self.dictionary.breadcrumbs()
        yield (self.url(), self.word_html())

    def get_string(self):
        homonym = self.get_homonym()
        if homonym:
            return format_html('{}<sub>{}</sub>', str(self), homonym)
        else:
            return str(self)

    def get_classes(self):
        return ['word', self.dictionary.language.code]

    def word_html(self, word=''):
        return format_html(
            '<span class="{}">{}</span>', ' '.join(self.get_classes()), word or self.get_string())

    def gloss_html(self, gloss=''):
        return format_html('<span class="gloss">{}</span>', gloss or self.get_gloss())

    def html(self, word='', gloss=''):
        return format_html('{} {}', self.word_html(word), self.gloss_html(gloss))

    def link(self, word='', gloss=''):
        return format_html('<a href="{}">{}</a>', self.url(), self.html(word, gloss))

    def get_type(self):
        variants = self.variants.all()
        if variants:
            return variants[0].type
        else:
            return ''

    @admin.display(description='Gloss')
    def get_gloss(self):
        if self.gloss:
            return self.gloss
        else:
            variants = self.variants.all()
            if variants:
                return variants[0].get_gloss()
            else:
                return ''

    def get_variants(self):
        '''Used for ordering the variants.'''
        class_list = self.dictionary.get_class_list()
        return sorted(self.variants.all(), key=lambda variant: class_list.index(variant.lexclass))


class Variant(models.Model):
    TYPES = [
        ('r', 'Root'),
        ('s', 'Stem'),
        ('w', 'Word'),
        ('pf', 'Prefix'),
        ('if', 'Infix'),
        ('sf', 'Suffix'),
        ('cf', 'Circumfix'),
        ('pc', 'Proclitic'),
        ('ec', 'Enclitic'),
    ]
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='variants', related_query_name='variant')
    type = models.CharField(max_length=2, choices=TYPES, default='s')
    lexclass = models.CharField('class', max_length=20)
    form = models.CharField(max_length=50, blank=True)
    extra_forms = models.TextField(blank=True)
    definition = models.TextField()
    notes = models.TextField(blank=True)
    # derivatives

    def __str__(self):
        return self.get_form()

    def html(self):
        return self.word.html(word=self.get_form(), gloss=self.get_gloss())

    def link(self):
        return format_html('<a href="{}">{}</a>', self.word.url(), self.html())

    def get_lexclass(self):
        return self.word.dictionary.get_class_dict().get(self.lexclass, 'Unknown')

    def get_definitions(self):
        return self.definition.splitlines() or ['']

    def get_derivatives(self):
        return [derivative for derivative in self.derivatives.all() if derivative.kind not in DERIVATIONS]

    def get_descendents(self):
        return [derivative for derivative in self.derivatives.all() if derivative.kind in DERIVATIONS]

    def get_form(self):
        return self.form or self.word.citation()

    def get_forms(self):
        langcode = self.word.dictionary.language.code
        form_markup = f'$word[{langcode}]{{ {self.get_form()} }}'
        if self.extra_forms:
            return f'{form_markup}, {self.extra_forms}'
        else:
            return form_markup

    def get_gloss(self):
        return self.get_definitions()[0].split(',', maxsplit=1)[0]


class Etymology(models.Model):
    word = models.OneToOneField(Word, on_delete=models.CASCADE)
    kind = models.CharField(max_length=7)
    notes = models.TextField(blank=True)
    components = models.ManyToManyField(Variant, related_name='derivatives', related_query_name='derivative')
    order = models.TextField()

    def html(self):
        kind, prep = self.word.dictionary.get_derivation_dict().get(self.kind, ('', ''))
        if kind:
            kind = kind.capitalize()
            components = [component.link() for component in self.get_components()]
            if len(components) == 0:
                etymology = f'{kind}.'
            else:
                if len(components) == 1:
                    components_html = components[0]
                elif len(components) == 2:
                    components_html = mark_safe(' and '.join(components))
                else:
                    last = components.pop()
                    components_html = mark_safe(', '.join(components) + f', and {last}')
                etymology = format_html('{} {} {}.', kind, prep, components_html)
        else:
            etymology = 'Unknown etymology.'
        if self.notes:
            etymology = format_html('<p>{}</p><p>{}</p>', etymology, self.notes)
        return etymology

    def get_components(self):
        components = list(self.components.all())
        return [components[int(i)] for i in self.order.split(',')]
