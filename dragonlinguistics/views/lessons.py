from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.text import slugify
from django.views.generic import TemplateView

from . import base
from .langs import LangMixin
from .. import forms, models

# Views
class LessonsMixin:
    def dispatch(self, request, lang, slug, **kwargs):
        try:
            article = models.Article.get(slug=f'{lang.code.lower()}-lesson-{slug}')
        except models.Article.DoesNotExist:
            return redirect('langs:lessons:list', code=lang.code)
        else:
            return super().dispatch(request, lang=lang, article=article, **kwargs)


class List(LangMixin, base.PageMixin, TemplateView):
    template_name = 'dragonlinguistics/lessons/list.html'

    def get_object_list(self, lang):
        return models.Article.objects.filter(
            folder=models.Folder.objects.get(path=f'langs/{lang.code}/lessons')
        )


class New(LoginRequiredMixin, LangMixin, base.NewEdit):
    template_name = 'dragonlinguistics/lessons/new.html'
    forms = {'articleform': (forms.SpecialArticle, 'article')}

    def handle_forms(self, request, lang, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/lessons')
        article.slug = f'{lang.code.lower()}-lesson-{slugify(article.title)}'
        article.save()
        return redirect('langs:lessons:view', code=lang.code, slug=slugify(article.title))


class View(LangMixin, LessonsMixin, TemplateView):
    template_name = 'dragonlinguistics/lessons/view.html'


class Edit(LoginRequiredMixin, LangMixin, LessonsMixin, base.NewEdit):
    template_name = 'dragonlinguistics/lessons/edit.html'
    forms = {'articleform': (forms.SpecialArticle, 'article')}

    def handle_forms(self, request, lang, article, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/lessons')
        article.slug = f'{lang.code.lower()}-lesson-{slugify(article.title)}'
        article.save()
        return redirect('langs:lessons:view', code=lang.code, slug=slugify(article.title))


class Delete(LoginRequiredMixin, LangMixin, LessonsMixin, TemplateView):
    template_name = 'dragonlinguistics/lessons/delete.html'

    def post(self, request, lang, article):
        article.delete()
        return redirect('langs:lessons:list', code=lang.code)
