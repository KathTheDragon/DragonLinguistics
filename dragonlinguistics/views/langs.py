from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView

from . import base
from .. import forms, models

# Views
class LangMixin:
    def dispatch(self, request, code, **kwargs):
        try:
            lang = models.Language.objects.get(code=code)
        except models.Language.DoesNotExist:
            if request.method == 'GET':
                return redirect('langs:list')
            else:
                raise Http404
        else:
            return super().dispatch(request, lang=lang, **kwargs)


class List(base.PageMixin, base.SearchMixin, TemplateView):
    template_name = 'dragonlinguistics/langs/list.html'
    form = forms.LanguageSearch

    def get_object_list(self):
        query = self.request.GET
        return models.Language.objects.filter(
            **base.fuzzysearch(
                name=query.get('name', ''),
                code=query.get('code', '')
            )
        )


class Search(base.Search):
    template_name = 'dragonlinguistics/langs/search.html'
    target_url = 'langs:list'
    form = forms.LanguageSearch


class New(LoginRequiredMixin, base.NewEdit):
    template_name = 'dragonlinguistics/langs/new.html'
    forms = {'langform': (forms.Language, 'lang')}

    def handle_forms(self, request, langform):
        lang = langform.save()
        langfolder = models.Folder(
            parent=models.Folder.objects.get(path='langs'),
            path=f'langs/{lang.code}'
        )
        langfolder.save()
        models.Folder(parent=langfolder, path=f'langs/{lang.code}/grammar').save()
        return redirect(lang.get_absolute_url())


class View(LangMixin, TemplateView):
    template_name = 'dragonlinguistics/langs/view.html'


class Edit(LoginRequiredMixin, LangMixin, base.NewEdit):
    template_name = 'dragonlinguistics/langs/edit.html'
    forms = {'langform': (forms.Language, 'lang')}

    def handle_forms(self, request, lang, langform):
        oldcode = lang.code
        lang = langform.save()
        for folder in models.Folder.objects.filter(path__startswith=f'langs/{oldcode}'):
            folder.path.replace(f'langs/{oldcode}', f'langs/{lang.code}')
            folder.save()
        return redirect(lang.get_absolute_url())


class Delete(LoginRequiredMixin, LangMixin, TemplateView):
    template_name = 'dragonlinguistics/langs/delete.html'

    def post(self, request, lang):
        lang.delete()
        models.Folder.objects.get(path=f'langs/{lang.code}').delete()
        return redirect('langs:list')
