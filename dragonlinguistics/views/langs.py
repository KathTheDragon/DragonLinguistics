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


class List(base.SearchMixin, TemplateView):
    template_name = 'dragonlinguistics/langs/list.html'
    form = forms.LanguageSearch

    def get_object_list(self, query):
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


class New(LoginRequiredMixin, TemplateView):
    template_name = 'dragonlinguistics/langs/new.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('langform', forms.Language())
        return super().get_context_data(**kwargs)

    def post(self, request):
        langform = forms.Language(request.POST)
        if langform.is_valid():
            lang = langform.save()
            return redirect(lang.get_absolute_url())
        else:
            return self.get(request, langform=langform)


class View(LangMixin, TemplateView):
    template_name = 'dragonlinguistics/langs/view.html'


class Edit(LoginRequiredMixin, LangMixin, TemplateView):
    template_name = 'dragonlinguistics/langs/edit.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('langform', forms.Language(instance=kwargs.get('lang')))
        return super().get_context_data(**kwargs)

    def post(self, request, lang):
        langform = forms.Language(request.POST, instance=lang)
        if langform.is_valid():
            lang = langform.save()
            return redirect(lang.get_absolute_url())
        else:
            return self.get(request, lang=lang, langform=langform)


class Delete(LoginRequiredMixin, LangMixin, TemplateView):
    template_name = 'dragonlinguistics/langs/delete.html'

    def post(self, request, lang):
        lang.delete()
        return redirect('langs:list')
