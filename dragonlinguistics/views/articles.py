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
        if slug is None:
            return super().get_kwargs(**kwargs)
        else:
            return super().get_kwargs(article=models.Article.objects.get(slug=slug), **kwargs)


class List(ArticleMixin, base.List):
    def get_object_list(self, **kwargs):
        return models.Article.objects.all()


class New(LoginRequiredMixin, ArticleMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, articleform):
        article = articleform.save(commit=False)
        article.slug = slugify(article.title)
        article.save()
        return redirect('articles:view', slug=article.slug)


class View(ArticleMixin, base.Base):
    pass


class Edit(LoginRequiredMixin, ArticleMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, articleform):
        article = articleform.save(commit=False)
        article.slug = slugify(article.title)
        article.save()
        return redirect('articles:view', slug=article.slug)


class Delete(LoginRequiredMixin, ArticleMixin, base.Base):
    def post(self, request, article):
        article.delete()
        return redirect('articles:list')
