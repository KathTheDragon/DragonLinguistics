import builtins
from django import template

from common import utils

register = template.Library()

@register.filter
def str(obj):
    return builtins.str(obj)

@register.filter
@template.defaultfilters.stringfilter
def splitlines(s):
    return s.split('\n')

@register.filter
def min(m, n):
    return n if m < n else m

@register.filter
def max(m, n):
    return n if m > n else m

@register.filter
@template.defaultfilters.stringfilter
def endswith(string, suffix):
    return string.endswith(suffix)

@register.filter
@template.defaultfilters.stringfilter
def lstrip(string, chars):
    return string.lstrip(chars)

@register.filter
@template.defaultfilters.stringfilter
def singular(string, countnoun):
    if string.endswith('s'):
        return string[:-1]
    else:
        return f'{string} {countnoun}'

@register.filter
@template.defaultfilters.stringfilter
def plural(string, countnouns):
    if string.endswith('s'):
        return string
    else:
        return f'{string} {countnouns}'

@register.filter
@template.defaultfilters.stringfilter
def pluralise(string):
    return utils.pluralise(string)


@register.filter
def hasattr(obj, name):
    return builtins.hasattr(obj, name)
