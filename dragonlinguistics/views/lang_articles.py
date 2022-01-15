from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.text import slugify

from . import base
from .langs import LangMixin
from .. import forms, models

# Views
class LangArticleMixin(LangMixin):
    folder = 'langs/articles'

    def path(self, code, type):
        path = 'langs/{code}/{type}'.format(code=code, type=type)
        if path.endswith('articles'):
            path = path[:-9]
        return path.rstrip('/')

    def get_kwargs(self, slug=None, **kwargs):
        folder = models.Folder.objects.get(path=self.path(**kwargs))
        if slug is None:
            return super().get_kwargs(folder=folder, **kwargs)
        else:
            article = models.Article.objects.get(folder=folder, slug=slug)
            return super().get_kwargs(folder=folder, article=article, **kwargs)


class List(LangArticleMixin, base.List):
    def get_object_list(self, lang, folder, type, **kwargs):
        return models.Article.objects.filter(folder=folder)


class New(LoginRequiredMixin, LangArticleMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, lang, folder, type, articleform):
        article = articleform.save(commit=False)
        article.folder = folder
        article.slug = slugify(article.title)
        article.save()
        return redirect(article)


class View(LangArticleMixin, base.Base):
    pass


class Edit(LoginRequiredMixin, LangArticleMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, lang, folder, type, article, articleform):
        article = articleform.save(commit=False)
        article.slug = slugify(article.title)
        article.save()
        return redirect(article)


class Delete(LoginRequiredMixin, LangArticleMixin, base.Base):
    def post(self, request, lang, folder, type, article):
        article.delete()
        return redirect(folder)
