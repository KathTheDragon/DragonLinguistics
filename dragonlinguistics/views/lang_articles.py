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
        if slug is None:
            return super().get_kwargs(**kwargs)
        else:
            article = models.Article.objects.get(folder__path=self.path(**kwargs), slug=slug)
            return super().get_kwargs(article=article, **kwargs)


class List(LangArticleMixin, base.List):
    def get_object_list(self, lang, type, **kwargs):
        return models.Article.objects.filter(folder__path=self.path(code=lang.code, type=type))


class New(LoginRequiredMixin, LangArticleMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, lang, type, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=self.path(code=lang.code, type=type))
        article.slug = slugify(article.title)
        article.save()
        return redirect(article)


class View(LangArticleMixin, base.Base):
    pass


class Edit(LoginRequiredMixin, LangArticleMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, lang, type, article, articleform):
        article = articleform.save(commit=False)
        article.slug = slugify(article.title)
        article.save()
        return redirect(article)


class Delete(LoginRequiredMixin, LangArticleMixin, base.Base):
    def post(self, request, lang, type, article):
        article.delete()
        return redirect('langs:articles:list', code=lang.code, type=type)
