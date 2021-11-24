from django import template
from django.http import QueryDict

register = template.Library()

@register.simple_tag
def update_query(query=None, **kwargs):
    if query is None:
        query = QueryDict(mutable=True)
    else:
        query = query.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query
