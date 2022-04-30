import markup as _markup
from html import escape
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from . import nodes

register = Library()

@register.simple_tag
def markup(value, depth=0):
    value = conditional_escape(value, quote=False)
    return mark_safe(Markup().parse(value, depth=depth))


# Reimplement conditional_escape to be able to not escape quotes
def conditional_escape(text, quote=True):
    if hasattr(text, '__html__'):
        return text.__html__()
    else:
        return mark_safe(escape(str(text), quote=quote))


class Markup(_markup.Markup):
    def __init__(self):
        super().__init__()
        self.nodes['$'] |= nodes.nodes
        self.nodes['@'] = nodes.objects
