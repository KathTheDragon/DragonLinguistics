from django.db import models
from django.utils.safestring import mark_safe

from .langs import Language

class Word(models.Model):
    TYPES = [
        ('r', 'Root'),
        ('br', 'Bound Root'),
        ('s', 'Stem'),
        ('pf', 'Prefix'),
        ('if', 'Infix'),
        ('sf', 'Suffix'),
        ('cf', 'Circumfix'),
        ('pc', 'Proclitic'),
        ('ec', 'Enclitic'),
    ]
    lang = models.ForeignKey(Language, verbose_name='language', on_delete=models.CASCADE)
    lemma = models.CharField(max_length=50)
    homonym = models.IntegerField(default=0)
    type = models.CharField(max_length=2, choices=TYPES, default='s')
    notes = models.TextField(blank=True)
    etymology = models.TextField(blank=True)

    class Meta:
        ordering = ['lemma', 'id']
        constraints = [
            models.UniqueConstraint(fields=['lang', 'lemma', 'homonym'], name='unique-homonym')
        ]

    def save(self, *args, **kwargs):
        self.homonym = self.id
        super().save(*args, **kwargs)

    def get_homonym(self):
        ids = [
            id for (id,) in
            Word.objects.filter(lang=self.lang, lemma=self.lemma).values_list('id')
        ]
        if ids == [self.id]:
            return 0
        else:
            return ids.index(self.id) + 1

    def __str__(self):
        from django.utils.html import format_html
        citation = {
            'br': '*{}',
            'pf': '{}-',
            'if': '<{}>',
            'sf': '-{}',
            'pc': '{}=',
            'ec': '={}',
        }.get(self.type, '{}').format(self.lemma)
        homonym = self.get_homonym()
        if homonym:
            return format_html(
                '{}<sub>{}</sub>',
                citation,
                homonym
            )
        else:
            return citation

    def firstgloss(self):
        senses = self.sense_set.all()
        if senses:
            return senses[0].gloss
        else:
            return ''
    firstgloss.short_description = 'Gloss'

    def urls(self, action):
        from django.urls import reverse
        homonym = self.get_homonym()
        if homonym:
            return reverse(
                f'langs:words:{action}-homonym',
                kwargs={'code': self.lang.code, 'lemma': self.lemma, 'homonym': homonym}
            )
        else:
            return reverse(
                f'langs:words:{action}',
                kwargs={'code': self.lang.code, 'lemma': self.lemma}
            )

    def get_absolute_url(self):
        return self.urls('view')

    def get_edit_url(self):
        return self.urls('edit')

    def get_delete_url(self):
        return self.urls('delete')

    def get_classes(self):
        return mark_safe(f'"word {self.lang.code}"')


class Sense(models.Model):
    # Kinda want this to be language-specific
    POS = [
        ('aff', 'Affix'),
        ('adj', 'Adjective'),
        ('adp', 'Adposition'),
        ('adv', 'Adverb'),
        ('conj', 'Conjunction'),
        ('det', 'Determiner'),
        ('intj', 'Interjection'),
        ('n', 'Noun'),
        ('num', 'Numeral'),
        ('part', 'Particle'),
        ('pron', 'Pronoun'),
        ('pn', 'Proper Noun'),
        ('unk', 'Unknown'),
        ('v', 'Verb'),
    ]
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    gloss = models.CharField(max_length=20)
    defin = models.TextField('definition', blank=True)
    pos = models.CharField('part of speech', max_length=4, choices=POS, default='unk')
    grammclass = models.CharField('class', max_length=20, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.gloss
