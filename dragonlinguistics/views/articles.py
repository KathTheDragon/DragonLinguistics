from django.shortcuts import redirect

from . import base
from .. import forms, models

# Views
class ArticleMixin:
    parts = ['articles']
    instance = 'article'
    path_fmt = ''

    def path(self, **kwargs):
        path = self.path_fmt.format(**kwargs)
        if path.endswith('articles'):
            path = path[:9]
        return path.rstrip('/')

    def get_kwargs(self, slug=None, **kwargs):
        folder = models.Folder.objects.get(path=self.path(**kwargs))
        if slug is None:
            return super().get_kwargs(folder=folder, **kwargs)
        else:
            article = models.Article.objects.get(folder=folder, slug=slug)
            return super().get_kwargs(folder=folder, article=article, **kwargs)

    def get_breadcrumbs(self, folder, type='articles', article=None, **kwargs):
        from django.urls import reverse
        breadcrumbs = super().get_breadcrumbs(**kwargs)
        breadcrumbs.append((type.capitalize(), folder.get_absolute_url()))
        if article is not None:
            breadcrumbs.append((article.html(), article.get_absolute_url()))
        return breadcrumbs


class List(base.Actions):
    class List(ArticleMixin, base.List):
        def get_object_list(self, folder, **kwargs):
            return models.Article.objects.filter(folder=folder)

    class New(ArticleMixin, base.NewEdit):
        forms = {'articleform': forms.EditArticle}

        def handle_forms(self, request, folder, articleform, **kwargs):
            article = articleform.save(commit=False)
            article.folder = folder
            article.save()
            return article

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('New', ''))
            return breadcrumbs


class View(base.Actions):
    class View(ArticleMixin, base.Base):
        pass

    class Edit(ArticleMixin, base.NewEdit):
        forms = {'articleform': forms.EditArticle}

        def handle_forms(self, request, folder, article, articleform, **kwargs):
            return articleform.save()

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
