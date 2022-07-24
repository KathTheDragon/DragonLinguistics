import re

from django.db import models
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


class Dictionary(BaseModel):
    language = models.OneToOneField(Language, on_delete=models.CASCADE)
    classes = models.TextField('lexical classes', blank=True)
    order = models.TextField('alphabetical order', blank=True)  # Not using yet

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

    def url(self):
        return reverse('view-dictionary', kwargs={'name': self.language.name}, host=self.language.get_host())


class Word(BaseModel):
    TYPES = [
        ('r', 'Root'),
        ('s', 'Stem'),
        ('pf', 'Prefix'),
        ('if', 'Infix'),
        ('sf', 'Suffix'),
        ('cf', 'Circumfix'),
        ('pc', 'Proclitic'),
        ('ec', 'Enclitic'),
    ]
    dictionary = models.ForeignKey(Dictionary, related_name='words', related_query_name='word', on_delete=models.CASCADE, null=True)
    lemma = models.CharField(max_length=50)
    type = models.CharField(max_length=2, choices=TYPES, default='s')
    isunattested = models.BooleanField(default=False)
    etymology = models.TextField(blank=True)
    descendents = models.TextField(blank=True)
    references = models.TextField(blank=True)

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
        from django.utils.html import format_html
        citation = self.citation()
        homonym = self.get_homonym()
        if homonym:
            return format_html(
                '{}<sub>{}</sub>',
                citation,
                homonym
            )
        else:
            return citation

    def citation(self):
        citation = {
            'r': '√{}',
            'pf': '{}-',
            'if': '<{}>',
            'sf': '-{}',
            'pc': '{}=',
            'ec': '={}',
        }.get(self.type, '{}').format(self.lemma)
        if self.isunattested:
            citation = '*' + citation
        return citation

    def definition(self):
        variants = self.variants.all()
        if variants:
            return str(variants[0])
        else:
            return ''
    definition.short_description = 'Definition'

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

    def get_classes(self):
        return ['word', self.dictionary.language.code]


class Variant(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='variants', related_query_name='variant')
    lexclass = models.CharField('class', max_length=20)
    forms = models.TextField(blank=True)
    definition = models.TextField()
    notes = models.TextField(blank=True)
    derivatives = models.TextField(blank=True)

    def __str__(self):
        return self.get_definitions()[0]

    def get_lexclass(self):
        return self.word.dictionary.get_class_dict().get(self.lexclass, 'Unknown')

    def get_definitions(self):
        return self.definition.splitlines() or ['']

    def get_derivatives(self):
        return self.derivatives.splitlines()

    def get_classes(self):
        return self.word.get_classes()

    def get_string(self):
        return self.forms or self.word.citation
