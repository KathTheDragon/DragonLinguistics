from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.text import slugify

from . import base
from .langs import LangMixin
from .. import forms, models

# Views
class TextsMixin(LangMixin):
    folder = 'texts'

    def get_kwargs(self, code, slug=None, **kwargs):
        if slug is None:
            return super().get_kwargs(code=code, **kwargs)
        else:
            article = models.Article.objects.get(slug=f'{code.lower()}-text-{slug}')
            return super().get_kwargs(code=code, article=article, **kwargs)


class List(TextsMixin, base.List):
    def get_object_list(self, lang, **kwargs):
        return models.Article.objects.filter(
            folder=models.Folder.objects.get(path=f'langs/{lang.code}/texts')
        )


class New(LoginRequiredMixin, TextsMixin, base.NewEdit):
    forms = {'articleform': (forms.SpecialArticle, 'article')}

    def handle_forms(self, request, lang, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/texts')
        article.slug = f'{lang.code.lower()}-text-{slugify(article.title)}'
        article.save()
        return redirect('langs:texts:view', code=lang.code, slug=slugify(article.title))


class View(TextsMixin, base.Base):
    pass


class Edit(LoginRequiredMixin, TextsMixin, base.NewEdit):
    forms = {'articleform': (forms.SpecialArticle, 'article')}

    def handle_forms(self, request, lang, article, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/texts')
        article.slug = f'{lang.code.lower()}-text-{slugify(article.title)}'
        article.save()
        return redirect('langs:texts:view', code=lang.code, slug=slugify(article.title))


class Delete(LoginRequiredMixin, TextsMixin, base.Base):
    def post(self, request, lang, article):
        article.delete()
        return redirect('langs:texts:list', code=lang.code)
