from django import template

register = template.Library()

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