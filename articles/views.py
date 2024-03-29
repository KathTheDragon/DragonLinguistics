from typing import Any

from common import views as base
from common.shortcuts import get_object_or_404
from .models import Folder, Article

def process_folder_kwargs(view, **kwargs) -> dict[str, Any]:
    folder, _ = Folder.objects.get_or_create(path=view.article_folder.format(**kwargs))
    return {'folder': folder}


def process_article_kwargs(view, slug: str, **kwargs) -> dict[str, Any]:
    kwargs = process_folder_kwargs(view, **kwargs)
    return kwargs | {
        'article': get_object_or_404(Article, folder=kwargs['folder'], slug=slug),
    }


class ListArticles(base.Actions):
    template_folder = 'articles'
    article_folder = ''
    process_kwargs = staticmethod(process_folder_kwargs)

    class List(base.List):
        instance = 'article'

        def get_object_list(self, folder: str, **kwargs) -> Article:
            return Article.objects.filter(folder=folder)

        def get_context_data(self, **kwargs) -> dict[str, Any]:
            return super().get_context_data(**kwargs) | {'title': kwargs['folder'].kind().title()}


class ViewArticle(base.Actions):
    template_folder = 'articles'
    article_folder = ''
    process_kwargs = staticmethod(process_article_kwargs)

    class View(base.View):
        instance = 'article'

        def get_context_data(self, **kwargs) -> dict[str, Any]:
            return super().get_context_data(**kwargs) | {'no_content_header': True}
