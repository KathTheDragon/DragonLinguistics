from django.shortcuts import redirect

from common import views as base
from common.shortcuts import get_object_or_404
from .forms import NewArticle, EditArticle
from .models import Folder, Article

def process_folder_kwargs(view, **kwargs):
    folder, _ = Folder.objects.get_or_create(path=view.article_folder.format(**kwargs))
    return {'folder': folder}


def process_article_kwargs(view, slug, **kwargs):
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

        def get_object_list(self, folder, **kwargs):
            return Article.objects.filter(folder=folder)

    class New(base.New):
        form = NewArticle
        instance = 'article'
        parent = 'folder'


class ViewArticle(base.Actions):
    template_folder = 'articles'
    article_folder = ''
    process_kwargs = staticmethod(process_article_kwargs)

    class View(base.View):
        instance = 'article'

    class Edit(base.Edit):
        form = EditArticle
        instance = 'article'

    class Delete(base.Delete):
        instance = 'article'
