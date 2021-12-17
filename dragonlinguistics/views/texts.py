from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.text import slugify

from . import base
from .langs import LangMixin
from .. import forms, models

# Views
class TextsMixin:
    def dispatch(self, request, lang, slug, **kwargs):
        try:
            article = models.Article.objects.get(slug=f'{lang.code.lower()}-text-{slug}')
        except models.Article.DoesNotExist:
            return redirect('langs:texts:list', code=lang.code)
        else:
            return super().dispatch(request, lang=lang, article=article, **kwargs)


class List(LangMixin, base.List):
    folder = 'texts'

    def get_object_list(self, lang, **kwargs):
        return models.Article.objects.filter(
            folder=models.Folder.objects.get(path=f'langs/{lang.code}/texts')
        )


class New(LoginRequiredMixin, LangMixin, base.NewEdit):
    folder = 'texts'
    forms = {'articleform': (forms.SpecialArticle, 'article')}

    def handle_forms(self, request, lang, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/texts')
        article.slug = f'{lang.code.lower()}-text-{slugify(article.title)}'
        article.save()
        return redirect('langs:texts:view', code=lang.code, slug=slugify(article.title))


class View(LangMixin, TextsMixin, base.Base):
    folder = 'texts'


class Edit(LoginRequiredMixin, LangMixin, TextsMixin, base.NewEdit):
    folder = 'texts'
    forms = {'articleform': (forms.SpecialArticle, 'article')}

    def handle_forms(self, request, lang, article, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/texts')
        article.slug = f'{lang.code.lower()}-text-{slugify(article.title)}'
        article.save()
        return redirect('langs:texts:view', code=lang.code, slug=slugify(article.title))


class Delete(LoginRequiredMixin, LangMixin, TextsMixin, base.Base):
    folder = 'texts'

    def post(self, request, lang, article):
        article.delete()
        return redirect('langs:texts:list', code=lang.code)
