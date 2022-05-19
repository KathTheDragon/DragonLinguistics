from django.shortcuts import redirect

from common import views as base
from . import forms
from .models import Folder, Article

# Views
class ArticleMixin:
    parts = ['articles']
    folder = 'articles'
    instance = 'article'
    path_fmt = ''

    def path(self, **kwargs):
        path = self.path_fmt.format(**kwargs)
        if path.endswith('articles'):
            path = path[:9]
        return path.rstrip('/')

    def get_kwargs(self, slug=None, **kwargs):
        folder = Folder.objects.get(path=self.path(**kwargs))
        if slug is None:
            return super().get_kwargs(folder=folder, **kwargs)
        else:
            article = Article.objects.get(folder=folder, slug=slug)
            return super().get_kwargs(folder=folder, article=article, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.setdefault('type', 'article')
        kwargs.setdefault('citeable', True)
        return super().get_context_data(**kwargs)

    def get_breadcrumbs(self, folder, article=None, **kwargs):
        from django.urls import reverse
        breadcrumbs = super().get_breadcrumbs(**kwargs)
        breadcrumbs.append((kwargs.get('crumb', 'Articles'), folder.url()))
        if article is not None:
            breadcrumbs.append((article.html(), article.url()))
        return breadcrumbs


class List(base.Actions):
    class List(ArticleMixin, base.List):
        def get_object_list(self, folder, **kwargs):
            return Article.objects.filter(folder=folder)

    class New(ArticleMixin, base.NewEdit):
        forms = {'form': forms.NewArticle}

        def handle_forms(self, request, folder, form, **kwargs):
            article = form.save(commit=False)
            article.folder = folder
            article.save()
            return article

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('New', ''))
            return breadcrumbs


class View(base.Actions):
    class View(ArticleMixin, base.View):
        pass

    class Edit(ArticleMixin, base.NewEdit):
        forms = {'form': forms.EditArticle}

        def handle_forms(self, request, form, **kwargs):
            return form.save()

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Edit', ''))
            return breadcrumbs

    class Delete(ArticleMixin, base.Delete):
        def get_redirect_to(self, folder):
            return folder

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Delete', ''))
            return breadcrumbs
