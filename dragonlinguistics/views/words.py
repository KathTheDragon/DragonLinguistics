from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect

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
class WordMixin(LangMixin):
    folder = 'words'

    def get_kwargs(self, code, lemma=None, homonym=0, **kwargs):
        if lemma is None:
            return super().get_kwargs(code=code, **kwargs)
        else:
            word = models.Word.objects.get(lang__code=code, lemma=lemma, homonym=homonym)
            return super().get_kwargs(code=code, word=word, **kwargs)


class List(WordMixin, base.SearchMixin, base.List):
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


class Search(WordMixin, base.Search):
    target_url = 'langs:words:list'
    form = forms.WordSearch


class New(LoginRequiredMixin, WordMixin, base.NewEdit):
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


class View(WordMixin, base.Base):
    pass


class Edit(LoginRequiredMixin, LangMixin, WordMixin, base.NewEdit):
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


class Delete(LoginRequiredMixin, LangMixin, WordMixin, base.Base):
    def post(self, request, lang, word):
        lemma = word.lemma
        word.delete()
        correcthomonyms(lang, lemma)
        return redirect('langs:words:list', code=lang.code)
