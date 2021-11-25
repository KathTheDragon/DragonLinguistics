from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView

from . import base
from .langs import LangMixin
from .. import forms, models

# Helper functions
def correcthomonyms(lang, lemma):
    wordlist = list(models.Word.objects.filter(lang=lang, lemma=lemma))
    if not wordlist:
        pass
    elif len(wordlist) == 1:
        word = wordlist[0]
        word.homonym = 0
        word.save()
    else:
        for ix, word in enumerate(wordlist, start=1):
            if word.homonym != ix:
                word.homonym = ix
                word.save()


def setnewhomonym(lang, word):
    wordlist = models.Word.objects.filter(lang=lang, lemma=word.lemma)
    count = wordlist.count()
    if count == 0:
        word.homonym = 0
    elif count == 1:
        _word = wordlist.get()
        _word.homonym = 1
        _word.save()
        word.homonym = 2
    else:
        word.homonym = count+1
    word.save()


# Views
class WordMixin:
    def dispatch(self, request, lang, lemma, homonym=0, **kwargs):
        try:
            word = models.Word.objects.get(lang=lang, lemma=lemma, homonym=homonym)
        except models.Word.DoesNotExist:
            if request.method == 'GET':
                return base.redirect_params(
                    'langs:words:list',
                    kwargs={'code': lang.code},
                    params={'lemma': lemma}
                )
            else:
                raise Http404
        else:
            return super().dispatch(request, lang=lang, word=word, **kwargs)


class List(LangMixin, base.SearchMixin, base.List):
    template_name = 'dragonlinguistics/words/list.html'
    form = forms.WordSearch

    def get_object_list(self, lang, **kwargs):
        query = self.request.GET
        return models.Word.objects.filter(
            lang=lang,
            # word-level search terms
            **base.fuzzysearch(lemma=query.get('lemma', '')),
            **base.strictsearch(type=query.get('type', ''))
        ).filter(  # sense-level search terms
            **base.fuzzysearch(sense__gloss=query.get('gloss', ''))
        ).filter(
            **base.strictsearch(sense__pos=query.get('pos', ''))
        ).filter(
            **base.strictsearch(sense__grammclass__contains=query.get('classes', ''))
        )


class Search(LangMixin, base.Search):
    template_name = 'dragonlinguistics/words/search.html'
    target_url = 'langs:words:list'
    form = forms.WordSearch


class New(LoginRequiredMixin, LangMixin, base.NewEdit):
    template_name = 'dragonlinguistics/words/new.html'
    forms = {'wordform': (forms.Word, 'word'), 'senseformset': (forms.Senses, 'word')}
    extra_fields = ['addmore']

    def handle_forms(self, request, lang, wordform, senseformset, addmore):
        newword = wordform.save(commit=False)
        newword.lang = lang
        setnewhomonym(lang, newword)
        senses = senseformset.save(commit=False)
        for sense in senses:
            sense.word = newword
            sense.save()
        if addmore is not None:
            return self.get(request, lang=lang, addmore=addmore)
        else:
            return redirect(newword.get_absolute_url())


class View(LangMixin, WordMixin, TemplateView):
    template_name = 'dragonlinguistics/words/view.html'


class Edit(LoginRequiredMixin, LangMixin, WordMixin, base.NewEdit):
    template_name = 'dragonlinguistics/words/edit.html'
    forms = {'wordform': (forms.Word, 'word'), 'senseformset': (forms.Senses, 'word')}

    def handle_forms(self, request, lang, word, wordform, senseformset):
        newword = wordform.save(commit=False)
        senseformset.save()
        if word.lemma == newword.lemma:
            newword.save()
        else:
            setnewhomonym(lang, newword)
            correcthomonyms(lang, word.lemma)
        return redirect(newword.get_absolute_url())


class Delete(LoginRequiredMixin, LangMixin, WordMixin, TemplateView):
    template_name = 'dragonlinguistics/words/delete.html'

    def post(self, request, lang, word):
        lemma = word.lemma
        word.delete()
        correcthomonyms(lang, lemma)
        return redirect('langs:words:list', code=lang.code)
