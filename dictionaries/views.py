from typing import Any

from common import views as base
from common.shortcuts import get_object_or_404
from languages.views import process_language_kwargs
from .models import Dictionary, Word

def process_dictionary_kwargs(view, name: str) -> dict[str, Any]:
    kwargs = process_language_kwargs(view, name)
    return kwargs | {'dictionary': get_object_or_404(Dictionary, language=kwargs['language'])}


def process_word_kwargs(view, name: str, lemma: str) -> dict[str, Any]:
    kwargs = process_dictionary_kwargs(view, name)
    homonym = 1
    if '-' in lemma:
        _lemma, _homonym = lemma.rsplit('-', maxsplit=1)
        if _homonym.isdecimal():
            lemma, homonym = _lemma, int(_homonym)
    return kwargs | {'word': get_object_or_404(Word, dictionary=kwargs['dictionary'], lemma=lemma, index=homonym-1)}


class ViewDictionary(base.Actions):
    template_folder = 'dictionary'
    process_kwargs = staticmethod(process_dictionary_kwargs)

    class View(base.PageMixin, base.View):
        instance = 'dictionary'

        def get_context_data(self, **kwargs) -> dict[str, Any]:
            return super().get_context_data(**kwargs) | {'type': 'word', 'title': str(kwargs['dictionary'])}

        def get_object_list(self, dictionary: Dictionary, **kwargs):
            return Word.objects.filter(dictionary=dictionary)


class ViewWord(base.Actions):
    template_folder = 'dictionary'
    process_kwargs = staticmethod(process_word_kwargs)

    class View(base.View):
        instance = 'word'
