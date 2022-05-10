from django.db import models

from . import base
from .langs import Language

class Dictionary(base.Model):
    language = models.OneToOneField(Language, on_delete=models.CASCADE)
    classes = models.TextField('lexical classes', blank=True)
    order = models.TextField('alphabetical order', blank=True)  # Not using yet

    def __str__(self):
        return 'Dictionary'

    def get_class_list(self):
        classes = []
        for line in self.classes.splitlines():
            parts = line.split(',')
            if len(parts) == 1:
                code, name, group = parts[0], parts[0], ''
            elif len(parts) == 2:
                code, name, group = parts[0], parts[1], ''
            else:
                code, name, group = parts[:3]
            classes.append((code.strip(), name.strip(), group.strip()))
        return classes

    def url(self):
        from django.urls import reverse
        return reverse('langs:words:list', kwargs={'code': self.language.code})


class Word(base.Model):
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
        from django.urls import reverse
        homonym = self.get_homonym()
        if homonym:
            return reverse(
                f'langs:words:view-homonym',
                kwargs={'code': self.dictionary.language.code, 'lemma': self.lemma, 'homonym': homonym}
            )
        else:
            return reverse(
                f'langs:words:view',
                kwargs={'code': self.dictionary.language.code, 'lemma': self.lemma}
            )

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
        for code, name, group in self.word.dictionary.get_class_list():
            if self.lexclass == code:
                if group:
                    return f'{group} ({name})'
                else:
                    return name
        return 'Unknown'

    def get_definitions(self):
        return self.definition.splitlines() or ['']
