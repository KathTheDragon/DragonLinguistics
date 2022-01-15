from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.text import slugify

from . import base
from .. import forms, models

# Views
class ArticleMixin:
    folder = 'articles'

    def get_kwargs(self, slug=None, **kwargs):
        folder, _ = models.Folder.objects.get_or_create(path='')
        if slug is None:
            return super().get_kwargs(folder=folder, **kwargs)
        else:
            article = models.Article.objects.get(folder=folder, slug=slug)
            return super().get_kwargs(folder=folder, article=article, **kwargs)


class List(ArticleMixin, base.List):
    def get_object_list(self, folder, **kwargs):
        return models.Article.objects.filter(folder=folder)


class New(LoginRequiredMixin, ArticleMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, folder, articleform):
        article = articleform.save(commit=False)
        article.folder = folder
        article.slug = slugify(article.title)
        article.save()
        return redirect(article)


class View(ArticleMixin, base.Base):
    pass


class Edit(LoginRequiredMixin, ArticleMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, folder, article, articleform):
        article = articleform.save(commit=False)
        article.slug = slugify(article.title)
        article.save()
        return redirect(article)


class Delete(LoginRequiredMixin, ArticleMixin, base.Base):
    def post(self, request, folder, article):
        article.delete()
        return redirect(folder)
