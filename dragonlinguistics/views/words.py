from django.shortcuts import redirect

from . import base
from .langs import LangMixin
from .. import forms, models
from ..utils.words import parse_csv

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
    parts = ['langs', 'words']
    instance = 'word'

    def get_kwargs(self, code, lemma=None, homonym=1, **kwargs):
        if lemma is None:
            return super().get_kwargs(code=code, **kwargs)
        else:
            word = models.Word.objects.filter(lang__code=code, lemma=lemma)[homonym-1]
            return super().get_kwargs(code=code, word=word, **kwargs)

    def get_breadcrumbs(self, lang, word=None, **kwargs):
        from django.urls import reverse
        breadcrumbs = super().get_breadcrumbs(lang=lang, **kwargs)
        breadcrumbs.append(('Dictionary', reverse('langs:words:list', kwargs={'code': lang.code})))
        if word is not None:
            breadcrumbs.append((word.html(), word.url()))
        return breadcrumbs


class List(base.Actions):
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
        form = forms.WordSearch

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Search', ''))
            return breadcrumbs

    class New(WordMixin, base.NewEdit):
        forms = {'wordform': forms.Word, 'senseformset': forms.Senses}

        def handle_forms(self, request, lang, wordform, senseformset):
            newword = wordform.save(commit=False)
            newword.lang = lang
            newword.save()
            senses = senseformset.save(commit=False)
            for sense in senses:
                sense.word = newword
                sense.save()
            return newword

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('New', ''))
            return breadcrumbs


class View(base.Actions):
    class View(WordMixin, base.Base):
        pass

    class Edit(WordMixin, base.NewEdit):
        forms = {'wordform': forms.Word, 'senseformset': forms.Senses}

        def handle_forms(self, request, lang, word, wordform, senseformset):
            newword = wordform.save()
            senseformset.save()
            return newword

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Edit', ''))
            return breadcrumbs

    class Delete(WordMixin, base.Delete):
        def get_redirect_kwargs(self, lang):
            return {'code': lang.code}

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Delete', ''))
            return breadcrumbs


class Import(WordMixin, base.SecureBase):
    def get_context_data(self, **kwargs):
        kwargs.setdefault('importform', forms.Import(initial={'delimiter': ',', 'quotechar': '"'}))
        return super().get_context_data(**kwargs)

    def post(self, request, lang):
        importform = forms.Import(request.POST, request.FILES)
        if importform.is_valid():
            try:
                entries = parse_csv(
                    file=importform.cleaned_data['file'],
                    delimiter=importform.cleaned_data['delimiter'],
                    quotechar=importform.cleaned_data['quotechar']
                )
            except csv.Error:
                return self.get(request, lang=lang, importform=importform)

            if importform.cleaned_data['action'] == 'replace':
                Word.objects.delete()
            for entry in entries:
                word = Word(**entry['word'])
                word.save()
                for sense in entry['senses']:
                    Sense(word=word, **sense).save()
        else:
            return self.get(request, lang=lang, importform=importform)

    def get_breadcrumbs(self, **kwargs):
        breadcrumbs = super().get_breadcrumbs(**kwargs)
        breadcrumbs.append(('Import', ''))
        return breadcrumbs
