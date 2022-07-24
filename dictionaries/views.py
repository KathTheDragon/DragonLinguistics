from django.shortcuts import redirect

from common import views as base
from common.shortcuts import get_object_or_404
from languages.views import process_language_kwargs
from .forms import EditDictionary, NewWord, EditWord, make_variants_formset
from .models import Dictionary, Word
# from .utils import parse_csv

def process_dictionary_kwargs(view, name, type):
    kwargs = process_language_kwargs(view, name, type)
    return kwargs | {'dictionary': get_object_or_404(Dictionary, language=kwargs['language'])}


def process_word_kwargs(view, name, type, lemma):
    kwargs = process_dictionary_kwargs(view, name, type)
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

        def get_object_list(self, dictionary, **kwargs):
            return Word.objects.filter(dictionary=dictionary)

    class Settings(base.Edit):
        form = EditDictionary
        instance = 'dictionary'

    # class Import(base.SecureAction):
    #     template_name = 'import-dictionary'

    # class Export(base.View):
    #     template_name = 'export-dictionary'

    class New(base.New):
        form = NewWord
        instance = 'word'
        parent = 'dictionary'

        def get_formset_class(self, dictionary, **kwargs):
            return make_variants_formset(dictionary)


class ViewWord(base.Actions):
    template_folder = 'dictionary'
    process_kwargs = staticmethod(process_word_kwargs)

    class View(base.View):
        instance = 'word'

    class Edit(base.Edit):
        form = EditWord
        instance = 'word'

        def get_formset_class(self, dictionary, **kwargs):
            return make_variants_formset(dictionary)

    class Delete(base.Delete):
        instance = 'word'
