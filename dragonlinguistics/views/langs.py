from django.shortcuts import redirect

from . import base
from .. import forms, models

# Views
class LangMixin:
    parts = ['langs']
    instance = 'lang'

    def get_kwargs(self, code=None, **kwargs):
        if code is None:
            return super().get_kwargs(**kwargs)
        else:
            return super().get_kwargs(lang=models.Language.objects.get(code=code), **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.setdefault('type', 'language')
        return super().get_context_data(**kwargs)

    def get_breadcrumbs(self, lang=None, **kwargs):
        from django.urls import reverse
        breadcrumbs = super().get_breadcrumbs(**kwargs)
        breadcrumbs.append(('Languages', reverse('langs:list')))
        if lang is not None:
            breadcrumbs.append((lang.html(), lang.url()))
        return breadcrumbs


class List(base.Actions):
    class List(base.SearchMixin, LangMixin, base.List):
        form = forms.LanguageSearch
        fieldname = 'code'

        def get_object_list(self, **kwargs):
            query = self.request.GET
            return models.Language.objects.filter(
                **base.fuzzysearch(
                    name=query.get('name', ''),
                    code=query.get('code', '')
                )
            )

    class Search(LangMixin, base.Search):
        form = forms.LanguageSearch

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Search', ''))
            return breadcrumbs

    class New(LangMixin, base.NewEdit):
        forms = {'form': forms.Language}

        def handle_forms(self, request, form):
            lang = form.save()
            models.Dictionary(language=lang).save()
            models.Folder.objects.get_or_create(path=f'langs/{lang.code}')
            models.Folder.objects.get_or_create(path=f'langs/{lang.code}/grammar')
            models.Folder.objects.get_or_create(path=f'langs/{lang.code}/lessons')
            models.Folder.objects.get_or_create(path=f'langs/{lang.code}/texts')
            return lang

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('New', ''))
            return breadcrumbs


class View(base.Actions):
    class View(LangMixin, base.View):
        def get_context_data(self, **kwargs):
            lang = kwargs['lang']
            kwargs['hasarticles'] = bool(models.Folder.objects.get(path=f'langs/{lang.code}').article_set.count())
            kwargs['hasgrammar'] = bool(models.Folder.objects.get(path=f'langs/{lang.code}/grammar').article_set.count())
            kwargs['haslessons'] = bool(models.Folder.objects.get(path=f'langs/{lang.code}/lessons').article_set.count())
            kwargs['hastexts'] = bool(models.Folder.objects.get(path=f'langs/{lang.code}/texts').article_set.count())
            return super().get_context_data(**kwargs)

    class Edit(LangMixin, base.NewEdit):
        forms = {'form': forms.Language}

        def handle_forms(self, request, lang, form, **kwargs):
            oldcode = lang.code
            lang = form.save()
            for folder in models.Folder.objects.filter(path__startswith=f'langs/{oldcode}'):
                folder.path = folder.path.replace(f'langs/{oldcode}', f'langs/{lang.code}')
                folder.save()
            return lang

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Edit', ''))
            return breadcrumbs

    class Delete(LangMixin, base.Delete):
        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Delete', ''))
            return breadcrumbs
