from django.shortcuts import redirect

from articles.views import process_folder_kwargs, process_article_kwargs, ListArticles, ViewArticle
from common import views as base
from common.shortcuts import get_object_or_404
from .forms import NewLanguage, EditLanguage
from .models import Language

def process_language_kwargs(view, name, type):
    return {'language': get_object_or_404(Language, name=name, type=type)}


def process_lang_folder_kwargs(view, name, type):
    kwargs = process_language_kwargs(view, name, type)
    return kwargs | process_folder_kwargs(view, **kwargs)


def process_lang_article_kwargs(view, name, type, slug):
    kwargs = process_language_kwargs(view, name, type)
    return kwargs | process_article_kwargs(view, slug, **kwargs)


class ListLanguages(base.Actions):
    template_folder = 'languages'

    @staticmethod
    def process_kwargs(self, type):
        return {'type': type}

    class List(base.List):
        instance = 'language'

        def get_object_list(self, type, **kwargs):
            return Language.objects.filter(type=type)

    class New(base.New):
        form = NewLanguage
        instance = 'language'

        def get_extra_attrs(self, type, **kwargs):
            return {'type': type}


class ViewLanguage(base.Actions):
    template_folder = 'languages'
    process_kwargs = staticmethod(process_language_kwargs)

    class View(base.View):
        instance = 'language'

    class Edit(base.Edit):
        form = EditLanguage
        instance = 'language'

    class Delete(base.Delete):
        instance = 'language'
