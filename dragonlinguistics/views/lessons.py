from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.text import slugify

from . import base
from .langs import LangMixin
from .. import forms, models

# Views
class LessonsMixin(LangMixin):
    folder = 'lessons'

    def get_kwargs(self, slug=None, **kwargs):
        if slug is None:
            return super().get_kwargs(**kwargs)
        else:
            code = kwargs['code']
            article = models.Article.objects.get(folder__path=f'langs/{code}/lessons', slug=slug)
            return super().get_kwargs(article=article, **kwargs)


class List(LessonsMixin, base.List):
    def get_object_list(self, lang, **kwargs):
        return models.Article.objects.filter(folder__path=f'langs/{lang.code}/lessons')


class New(LoginRequiredMixin, LessonsMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, lang, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}/lessons')
        article.slug = slugify(article.title)
        article.save()
        return redirect('langs:lessons:view', code=lang.code, slug=article.slug)


class View(LessonsMixin, base.Base):
    pass


class Edit(LoginRequiredMixin, LessonsMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, lang, article, articleform):
        article = articleform.save(commit=False)
        article.slug = slugify(article.title)
        article.save()
        return redirect('langs:lessons:view', code=lang.code, slug=article.slug)


class Delete(LoginRequiredMixin, LessonsMixin, base.Base):
    def post(self, request, lang, article):
        article.delete()
        return redirect('langs:lessons:list', code=lang.code)
