from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.text import slugify
from django.views.generic import TemplateView

from . import base
from .langs import LangMixin
from .. import forms, models

# Views
class TextsMixin:
    def dispatch(self, request, lang, slug, **kwargs):
        try:
            article = models.Article.get(slug=f'{lang.code.lower()}-text-{slug}')
        except models.Article.DoesNotExist:
            return redirect('langs:texts:list', code=lang.code)
        else:
            return super().dispatch(request, lang=lang, article=article, **kwargs)


class List(LangMixin, base.List):
    template_name = 'dragonlinguistics/texts/list.html'

    def get_object_list(self, lang):
        return models.Article.objects.filter(
            folder=models.Folder.objects.get(path=f'langs/{lang.code}/texts')
        )


class New(LoginRequiredMixin, LangMixin, base.NewEdit):
    template_name = 'dragonlinguistics/texts/new.html'
    forms = {'articleform': (forms.SpecialArticle, 'article')}

    def handle_forms(self, request, lang, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/texts')
        article.slug = f'{lang.code.lower()}-text-{slugify(article.title)}'
        article.save()
        return redirect('langs:texts:view', code=lang.code, slug=slugify(article.title))


class View(LangMixin, TextsMixin, TemplateView):
    template_name = 'dragonlinguistics/texts/view.html'


class Edit(LoginRequiredMixin, LangMixin, TextsMixin, base.NewEdit):
    template_name = 'dragonlinguistics/texts/edit.html'
    forms = {'articleform': (forms.SpecialArticle, 'article')}

    def handle_forms(self, request, lang, article, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/texts')
        article.slug = f'{lang.code.lower()}-text-{slugify(article.title)}'
        article.save()
        return redirect('langs:texts:view', code=lang.code, slug=slugify(article.title))


class Delete(LoginRequiredMixin, LangMixin, TextsMixin, TemplateView):
    template_name = 'dragonlinguistics/texts/delete.html'

    def post(self, request, lang, article):
        article.delete()
        return redirect('langs:texts:list', code=lang.code)
