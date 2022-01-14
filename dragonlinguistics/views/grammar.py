from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.text import slugify

from . import base
from .langs import LangMixin
from .. import forms, models

# Views
class GrammarMixin(LangMixin):
    folder = 'grammar'

    def get_kwargs(self, slug=None, **kwargs):
        if slug is None:
            return super().get_kwargs(**kwargs)
        else:
            code = kwargs['code']
            article = models.Article.objects.get(folder__path=f'langs/{code}/grammar', slug=slug)
            return super().get_kwargs(article=article, **kwargs)


class List(GrammarMixin, base.List):
    def get_object_list(self, lang, **kwargs):
        return models.Article.objects.filter(folder__path=f'langs/{lang.code}/grammar')


class New(LoginRequiredMixin, GrammarMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, lang, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/grammar')
        article.slug = slugify(article.title)
        article.save()
        return redirect('langs:grammar:view', code=lang.code, slug=article.slug)


class View(GrammarMixin, base.Base):
    pass


class Edit(LoginRequiredMixin, GrammarMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, lang, article, articleform):
        article = articleform.save(commit=False)
        article.slug = slugify(article.title)
        article.save()
        return redirect('langs:grammar:view', code=lang.code, slug=article.slug)


class Delete(LoginRequiredMixin, GrammarMixin, base.Base):
    def post(self, request, lang, article):
        article.delete()
        return redirect('langs:grammar:list', code=lang.code)
