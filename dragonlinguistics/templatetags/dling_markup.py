import re
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from ..models.langs import Language
from ..models.words import Word

register = Library()

@register.filter(needs_autoescape=True)
@stringfilter
def markup(value, lang=None, autoescape=True):
    if autoescape:
        value = conditional_escape(value)
    value = re.sub(
        r'\{lang:(?P<code>[a-z]{3,5})\}',
        lambda m: linklang(code=m['code']),
        value
    )
    value = re.sub(
        r'\{word:(?:(?P<code>[a-z]{3,5})/)?(?P<lemma>[^\d/}\r\n]+?)(?:/(?P<homonym>\d+))?\}',
        lambda m: linkword(lang, **m.groupdict()),
        value
    )
    value = re.sub(
        r'\{\*word:(?:(?P<code>[a-z]{3,5})/)?(?P<lemma>[^\d/}\r\n]+?)(?:/(?P<homonym>\d+))?\}',
        lambda m: writeword(lang, **m.groupdict()),
        value
    )
    return mark_safe(value)

def linklang(code):
    try:
        lang = Language.objects.get(code=code)
    except Language.DoesNotExist:
        return error('Invalid language code')
    else:
        return f'<a href="{lang.get_absolute_url()}" class="lang {code}">{lang}</a>'

def linkword(lang, code, lemma, homonym):
    if code:
        try:
            lang = Language.objects.get(code=code)
        except Language.DoesNotExist:
            return error('Invalid language code')
    elif lang is None:
        return error('No language code given')
    else:
        code = lang.code
    if homonym is None:
        homonym = 0
    try:
        word = Word.objects.get(lang=lang, lemma=lemma, homonym=homonym)
    except Word.DoesNotExist:
        return error('Invalid lemma/homonym number')
    else:
        return f'<a href="{word.get_absolute_url()}"><span class="word {code}">{word}</span> &quot;{word.firstgloss()}&quot;</a>'

def writeword(lang, code, lemma, homonym):
    if not code:
        if lang is None:
            code = ''
        else:
            code = lang.code
    if homonym is None:
        homonym = 0
    return f'<span class="word {code}">{lemma}</span>'

def error(msg):
    return f'<span class="error">{msg}</span>'
