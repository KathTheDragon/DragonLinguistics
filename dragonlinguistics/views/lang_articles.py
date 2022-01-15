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

    @property
    def path(self):
        path = self.folder.replace('langs/', 'langs/{code}')
        if path.endswith('/articles'):
            return path[:-9]
        else:
            return path

    @property
    def namespace(self):
        return self.folder.replace('/', ':')

    def get_kwargs(self, slug=None, **kwargs):
        if slug is None:
            return super().get_kwargs(**kwargs)
        else:
            article = models.Article.objects.get(folder__path=self.path.format(**kwargs), slug=slug)
            return super().get_kwargs(article=article, **kwargs)


class List(LangArticleMixin, base.List):
    def get_object_list(self, lang, **kwargs):
        return models.Article.objects.filter(folder__path=self.path.format(code=lang.code))


class New(LoginRequiredMixin, LangArticleMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, lang, articleform):
        article = articleform.save(commit=False)
        article.folder = models.Folder.objects.get(path=self.path.format(code=lang.code))
        article.slug = slugify(article.title)
        article.save()
        return redirect(article)


class View(LangArticleMixin, base.Base):
    pass


class Edit(LoginRequiredMixin, LangArticleMixin, base.NewEdit):
    forms = {'articleform': (forms.Article, 'article')}

    def handle_forms(self, request, lang, article, articleform):
        article = articleform.save(commit=False)
        article.slug = slugify(article.title)
        article.save()
        return redirect(article)


class Delete(LoginRequiredMixin, LangArticleMixin, base.Base):
    def post(self, request, lang, article):
        article.delete()
        return redirect(f'{self.namespace}:list', code=lang.code)
