from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.text import slugify

from . import base
from .langs import LangMixin
from .. import forms, models

# Views
class LangArticleMixin(LangMixin):
    folder = 'lang_articles'

    def get_kwargs(self, code, slug=None, **kwargs):
        if slug is None:
            return super().get_kwargs(code=code, **kwargs)
        else:
            article = models.Article.objects.get(folder__path=f'langs/{code}', slug=slug)
            return super().get_kwargs(code=code, article=article, **kwargs)


class List(LangArticleMixin, base.List):
    def get_object_list(self, lang, **kwargs):
        return models.Article.objects.filter(folder_path=f'langs/{lang.code}')


class New(LoginRequiredMixin, LangArticleMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, lang, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=f'langs/{lang.code}')
        article.slug = slugify(article.title)
        article.save()
        return redirect('langs:articles:view', code=lang.code, slug=article.slug)


class View(LangArticleMixin, base.Base):
    pass


class Edit(LoginRequiredMixin, LangArticleMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, lang, article, articleform):
        article = articleform.save(commit=False)
        article.slug = slugify(article.title)
        article.save()
        return redirect('langs:articles:view', code=lang.code, slug=article.slug)


class Delete(LoginRequiredMixin, LangArticleMixin, base.Base):
    def post(self, request, lang, article):
        article.delete()
        return redirect('langs:articles:list', code=lang.code)
