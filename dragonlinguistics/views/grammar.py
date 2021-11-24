from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.text import slugify
from django.views.generic import TemplateView

from . import base
from .langs import LangMixin
from .. import forms, models

# Views
class GrammarMixin:
    def dispatch(self, request, lang, slug, **kwargs):
        try:
            article = models.Article.objects.get(slug=f'{lang.code.lower()}-grammar-{slug}')
        except models.Article.DoesNotExist:
            return redirect('langs:grammar:list', code=lang.code)
        else:
            return super().dispatch(request, lang=lang, article=article, **kwargs)


class List(LangMixin, base.PageMixin, TemplateView):
    template_name = 'dragonlinguistics/grammar/list.html'

    def get_object_list(self, lang):
        return models.Article.objects.filter(
            folder=models.Folder.objects.get(path=f'langs/{lang.code}/grammar')
        )


class New(LoginRequiredMixin, LangMixin, base.NewEdit):
    template_name = 'dragonlinguistics/grammar/new.html'
    forms = {'articleform': (forms.SpecialArticle, 'article')}

    def handle_forms(self, request, lang, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/grammar')
        article.slug = f'{lang.code.lower()}-grammar-{slugify(article.title)}'
        article.save()
        return redirect('langs:grammar:view', code=lang.code, slug=slugify(article.title))


class View(LangMixin, GrammarMixin, TemplateView):
    template_name = 'dragonlinguistics/grammar/view.html'


class Edit(LoginRequiredMixin, LangMixin, GrammarMixin, base.NewEdit):
    template_name = 'dragonlinguistics/grammar/edit.html'
    forms = {'articleform': (forms.SpecialArticle, 'article')}

    def handle_forms(self, request, lang, article, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/grammar')
        article.slug = f'{lang.code.lower()}-grammar-{slugify(article.title)}'
        article.save()
        return redirect('langs:grammar:view', code=lang.code, slug=slugify(article.title))


class Delete(LoginRequiredMixin, LangMixin, GrammarMixin, TemplateView):
    template_name = 'dragonlinguistics/grammar/delete.html'

    def post(self, request, lang, article):
        article.delete()
        return redirect('langs:grammar:list', code=lang.code)
