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


class List(base.SearchMixin, LangMixin, base.List):
    form = forms.LanguageSearch

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


class New(LangMixin, base.NewEdit):
    forms = {'langform': forms.Language}

    def handle_forms(self, request, langform):
        lang = langform.save()
        models.Folder.objects.get_or_create(path=f'langs/{lang.code}')
        models.Folder.objects.get_or_create(path=f'langs/{lang.code}/grammar')
        models.Folder.objects.get_or_create(path=f'langs/{lang.code}/lessons')
        models.Folder.objects.get_or_create(path=f'langs/{lang.code}/texts')
        return lang


class View(LangMixin, base.Base):
    pass


class Edit(LangMixin, base.NewEdit):
    forms = {'langform': forms.Language}

    def handle_forms(self, request, lang, langform):
        oldcode = lang.code
        lang = langform.save()
        for folder in models.Folder.objects.filter(path__startswith=f'langs/{oldcode}'):
            folder.path = folder.path.replace(f'langs/{oldcode}', f'langs/{lang.code}')
            folder.save()
        return lang


class Delete(LangMixin, base.SecureBase):
    pass
