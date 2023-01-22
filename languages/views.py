from typing import Any

from articles.views import process_folder_kwargs, process_article_kwargs
from common import views as base
from common.shortcuts import get_object_or_404
from .models import Language

def get_language_type(view) -> str:
    return {
        'conlang': 'conlang',
        'hist': 'natlang',
    }.get(view.request.host.name)


def process_language_kwargs(view, name: str) -> dict[str, Any]:
    return {'language': get_object_or_404(Language, name=name, type=get_language_type(view))}


def process_lang_folder_kwargs(view, name: str) -> dict[str, Any]:
    kwargs = process_language_kwargs(view, name)
    return kwargs | process_folder_kwargs(view, **kwargs)


def process_lang_article_kwargs(view, name: str, slug: str) -> dict[str, Any]:
    kwargs = process_language_kwargs(view, name)
    return kwargs | process_article_kwargs(view, slug, **kwargs)


class ListLanguages(base.Actions):
    template_folder = 'languages'

    class List(base.List):
        instance = 'language'

        def get_object_list(self, **kwargs):
            return Language.objects.filter(type=get_language_type(self))

        def get_context_data(self, **kwargs) -> dict[str, Any]:
            return super().get_context_data(**kwargs) | {'title': 'Languages'}


class ViewLanguage(base.Actions):
    template_folder = 'languages'
    process_kwargs = staticmethod(process_language_kwargs)

    class View(base.View):
        instance = 'language'
