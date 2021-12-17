from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.text import slugify

from . import base
from .langs import LangMixin
from .. import forms, models

# Views
class LessonsMixin:
    def dispatch(self, request, lang, slug, **kwargs):
        try:
            article = models.Article.objects.get(slug=f'{lang.code.lower()}-lesson-{slug}')
        except models.Article.DoesNotExist:
            return redirect('langs:lessons:list', code=lang.code)
        else:
            return super().dispatch(request, lang=lang, article=article, **kwargs)


class List(LangMixin, base.List):
    folder = 'lessons'

    def get_object_list(self, lang, **kwargs):
        return models.Article.objects.filter(
            folder=models.Folder.objects.get(path=f'langs/{lang.code}/lessons')
        )


class New(LoginRequiredMixin, LangMixin, base.NewEdit):
    folder = 'lessons'
    forms = {'articleform': (forms.SpecialArticle, 'article')}

    def handle_forms(self, request, lang, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/lessons')
        article.slug = f'{lang.code.lower()}-lesson-{slugify(article.title)}'
        article.save()
        return redirect('langs:lessons:view', code=lang.code, slug=slugify(article.title))


class View(LangMixin, LessonsMixin, base.Base):
    folder = 'lessons'


class Edit(LoginRequiredMixin, LangMixin, LessonsMixin, base.NewEdit):
    folder = 'lessons'
    forms = {'articleform': (forms.SpecialArticle, 'article')}

    def handle_forms(self, request, lang, article, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/lessons')
        article.slug = f'{lang.code.lower()}-lesson-{slugify(article.title)}'
        article.save()
        return redirect('langs:lessons:view', code=lang.code, slug=slugify(article.title))


class Delete(LoginRequiredMixin, LangMixin, LessonsMixin, base.Base):
    folder = 'lessons'

    def post(self, request, lang, article):
        article.delete()
        return redirect('langs:lessons:list', code=lang.code)
