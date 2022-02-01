from django.shortcuts import redirect
from django.utils.text import slugify

from . import base
from .. import forms, models

# Views
class ArticleMixin:
    folder = 'articles'
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


class List(ArticleMixin, base.List):
    def get_object_list(self, folder, **kwargs):
        return models.Article.objects.filter(folder=folder)


class New(ArticleMixin, base.NewEdit):
    forms = {'articleform': (forms.NewArticle, 'article')}

    def handle_forms(self, request, folder, articleform, **kwargs):
        article = articleform.save(commit=False)
        article.folder = folder
        article.slug = slugify(article.title)
        article.save()
        return redirect(article)


class View(ArticleMixin, base.Base):
    pass


class Edit(ArticleMixin, base.NewEdit):
    forms = {'articleform': (forms.EditArticle, 'article')}

    def handle_forms(self, request, folder, article, articleform, **kwargs):
        article = articleform.save(commit=False)
        article.slug = slugify(article.title)
        article.save()
        return redirect(article)


class Delete(ArticleMixin, base.SecureBase):
    def post(self, request, folder, article, **kwargs):
        article.delete()
        return redirect(folder)
