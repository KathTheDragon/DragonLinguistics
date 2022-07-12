from django.shortcuts import redirect

from common import views as base
from languages.views.langs import LangMixin
from . import forms, models
from .models import Dictionary, Word, Variant
from .utils import parse_csv

# Views
class WordMixin(LangMixin):
    parts = ['langs', 'words']
    folder = 'words'
    instance = 'word'

    def get_kwargs(self, code, lemma=None, homonym=1, **kwargs):
        dictionary = Dictionary.objects.get(language__code=code)
        if lemma is None:
            return super().get_kwargs(code=code, dictionary=dictionary, **kwargs)
        else:
            word = Word.objects.filter(dictionary=dictionary, lemma=lemma)[homonym-1]
            return super().get_kwargs(code=code, dictionary=dictionary, word=word, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['type'] = 'word'
        return super().get_context_data(**kwargs)

    def get_breadcrumbs(self, dictionary, word=None, **kwargs):
        from django.urls import reverse
        breadcrumbs = super().get_breadcrumbs(**kwargs)
        breadcrumbs.append(('Dictionary', dictionary.url()))
        if word is not None:
            breadcrumbs.append((word.html(), word.url()))
        return breadcrumbs


class List(base.Actions):
    class List(WordMixin, base.SearchMixin, base.List):
        form = forms.Search
        fieldname = 'lemma'

        def get_folder(self):
            return self.folder

        def get_object_list(self, dictionary, **kwargs):
            query = self.request.GET
            return Word.objects.filter(
                dictionary=dictionary,
                # word-level search terms
                **base.fuzzysearch(lemma=query.get('lemma', '')),
                **base.strictsearch(type=query.get('type', ''))
            ).filter(  # Variant-level search terms
                **base.strictsearch(variant__definition__contains=query.get('definition', ''))
            ).filter(
                **base.strictsearch(variant__lexclass=query.get('class', ''))
            )

        def get_context_data(self, **kwargs):
            kwargs['title'] = f'{kwargs["lang"].name} Dictionary'
            return super().get_context_data(**kwargs)

    class Search(WordMixin, base.Search):
        form = forms.Search

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Search', ''))
            return breadcrumbs

    class Settings(WordMixin, base.NewEdit):
        instance = 'dictionary'
        forms = {'form': forms.Dictionary}

        def get_folder(self):
            return self.folder

        def handle_forms(self, request, form, **kwargs):
            return form.save()

    class New(WordMixin, base.NewEdit):
        use_addmore = True

        def get_forms(self, **kwargs):
            return {
                'form': forms.Word,
                'formset': forms.make_variants_formset(kwargs['dictionary']),
            }

        def handle_forms(self, request, dictionary, form, formset, **kwargs):
            newword = form.save(commit=False)
            newword.dictionary = dictionary
            newword.save()
            variants = formset.save(commit=False)
            for variant in variants:
                variant.word = newword
                variant.save()
            return newword

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('New', ''))
            return breadcrumbs

        def get_context_data(self, **kwargs):
            kwargs['formsetname'] = 'Variant'
            return super().get_context_data(**kwargs)

    class Import(WordMixin, base.SecureBase):
        def get_folder(self):
            return self.folder

        def get_context_data(self, **kwargs):
            kwargs.setdefault('importform', forms.Import(initial={'delimiter': ',', 'quotechar': '"'}))
            return super().get_context_data(**kwargs)

        def post(self, request, **kwargs):
            importform = forms.Import(request.POST, request.FILES)
            if importform.is_valid():
                try:
                    entries = parse_csv(
                        file=importform.cleaned_data['file'],
                        delimiter=importform.cleaned_data['delimiter'],
                        quotechar=importform.cleaned_data['quotechar']
                    )
                except csv.Error:
                    return self.get(request, importform=importform, **kwargs)

                dictionary = kwargs['dictionary']
                if importform.cleaned_data['action'] == 'replace':
                    Word.objects.filter(dictionary=dictionary).delete()
                for entry in entries:
                    word = Word(dictionary=dictionary, **entry['word'])
                    word.save()
                    for variant in entry['variants']:
                        Variant(word=word, **variant).save()
            else:
                return self.get(request, importform=importform, **kwargs)

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Import', ''))
            return breadcrumbs


class View(base.Actions):
    class View(WordMixin, base.View):
        pass

    class Edit(WordMixin, base.NewEdit):
        def get_forms(self, **kwargs):
            return {
                'form': forms.Word,
                'formset': forms.make_variants_formset(kwargs['dictionary']),
            }

        def handle_forms(self, request, form, formset, **kwargs):
            newword = form.save()
            formset.save()
            return newword

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Edit', ''))
            return breadcrumbs

        def get_context_data(self, **kwargs):
            kwargs['formsetname'] = 'Variant'
            return super().get_context_data(**kwargs)

    class Delete(WordMixin, base.Delete):
        def get_redirect_to(self, dictionary, **kwargs):
            return dictionary

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Delete', ''))
            return breadcrumbs
