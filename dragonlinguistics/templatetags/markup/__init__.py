from html import escape
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from .parse import parse

register = Library()

@register.filter(needs_autoescape=True)
@stringfilter
def markup(value, autoescape=True):
    if autoescape:
        value = conditional_escape(value, quote=False)
    return mark_safe(parse(value))


# Reimplement conditional_escape to be able to not escape quotes
def conditional_escape(text, quote=True):
    if hasattr(text, '__html__'):
        return text.__html__()
    else:
        return mark_safe(escape(str(text), quote=quote))
