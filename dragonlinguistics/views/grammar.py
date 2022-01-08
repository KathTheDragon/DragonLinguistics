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

    def get_kwargs(self, code, slug=None, **kwargs):
        if slug is None:
            return super().get_kwargs(code=code, **kwargs)
        else:
            article = models.Article.objects.get(slug=f'{code.lower()}-grammar-{slug}')
            return super().get_kwargs(code=code, article=article, **kwargs)


class List(GrammarMixin, base.List):
    def get_object_list(self, lang, **kwargs):
        return models.Article.objects.filter(
            folder=models.Folder.objects.get(path=f'langs/{lang.code}/grammar')
        )


class New(LoginRequiredMixin, GrammarMixin, base.NewEdit):
    forms = {'articleform': (forms.SpecialArticle, 'article')}

    def handle_forms(self, request, lang, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/grammar')
        article.slug = f'{lang.code.lower()}-grammar-{slugify(article.title)}'
        article.save()
        return redirect('langs:grammar:view', code=lang.code, slug=slugify(article.title))


class View(GrammarMixin, base.Base):
    pass


class Edit(LoginRequiredMixin, GrammarMixin, base.NewEdit):
    forms = {'articleform': (forms.SpecialArticle, 'article')}

    def handle_forms(self, request, lang, article, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/grammar')
        article.slug = f'{lang.code.lower()}-grammar-{slugify(article.title)}'
        article.save()
        return redirect('langs:grammar:view', code=lang.code, slug=slugify(article.title))


class Delete(LoginRequiredMixin, GrammarMixin, base.Base):
    def post(self, request, lang, article):
        article.delete()
        return redirect('langs:grammar:list', code=lang.code)
