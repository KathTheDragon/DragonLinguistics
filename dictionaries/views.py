from django.http import FileResponse, StreamingHttpResponse
from django.shortcuts import redirect
from urllib.parse import quote

from common import views as base
from common.shortcuts import get_object_or_404
from languages.views import process_language_kwargs
from . import forms
from .models import Dictionary, Word, Variant
from .utils import make_csv

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
        form = forms.EditDictionary
        instance = 'dictionary'
        redirects = base.Edit.redirects | {'edit': lambda obj: f'{obj.url()}?settings'}

    class Import(base.FormAction):
        template_name = 'import-dictionary'
        form = forms.ImportDictionary
        instance = 'dictionary'

        def handle_forms(self, form, formset, dictionary, **kwargs):
            action = form.cleaned_data['action']
            entries = form.cleaned_data['entries']
            if action == 'replace':
                Word.objects.filter(dictionary=dictionary).delete()
            for entry in entries:
                word = Word(dictionary=dictionary, **entry['word'])
                word.save()
                for variant in entry['variants']:
                    Variant(word=word, **variant).save()
            return dictionary

    class Export(base.FormAction):
        template_name = 'export-dictionary'
        form = forms.ExportDictionary
        instance = 'dictionary'

        def handle_forms(self, form, dictionary, **kwargs):
            return make_csv(dictionary, form.cleaned_data['delimiter'], form.cleaned_data['quotechar'])

        def get_response(self, request, entries, language, **kwargs):
            filename = f'{language.name}.csv'
            try:
                filename.encode('ascii')
                file_expr = 'filename="{}"'.format(filename)
            except UnicodeEncodeError:
                file_expr = "filename*=utf-8''{}".format(quote(filename))
            return StreamingHttpResponse(entries, content_type='text/csv', headers={
                'Content-Disposition': f'attachment; {file_expr}'})


    class New(base.New):
        form = forms.NewWord
        instance = 'word'
        parent = 'dictionary'

        def get_formset_class(self, dictionary, **kwargs):
            return forms.make_variants_formset(dictionary)


class ViewWord(base.Actions):
    template_folder = 'dictionary'
    process_kwargs = staticmethod(process_word_kwargs)

    class View(base.View):
        instance = 'word'

    class Edit(base.Edit):
        form = forms.EditWord
        instance = 'word'

        def get_formset_class(self, dictionary, **kwargs):
            return forms.make_variants_formset(dictionary)

    class Delete(base.Delete):
        instance = 'word'
