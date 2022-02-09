from django.shortcuts import redirect

from . import base
from .. import forms, models

class ReferenceMixin:
    parts = ['references']
    instance = 'reference'

    def get_kwargs(self, author=None, year=None, index=None, **kwargs):
        if author is None:
            return super().get_kwargs(**kwargs)
        else:
            reference = models.Reference.objects.filter(author=author, year=year)[index]
            return super().get_kwargs(reference=reference, **kwargs)


class List(base.SearchMixin, ReferenceMixin, base.Base):
    form = forms.ReferenceSearch

    def get_context_data(self, **kwargs):
        query = self.request.GET
        objectlist = models.Reference.objects.filter(
            **base.fuzzysearch(title=query.get('title', '')),
            **base.strictsearch(
                author__startswith=query.get('author', ''),
                year=int(query.get('year', '0'))
            ),
        )
        authors = objectlist.values_list('author').distinct()
        author_references = {}
        for (author,) in authors:
            author_references[author] = objectlist.filter(author=author)
        kwargs.setdefault('author_references', author_references)
        return super().get_context_data(**kwargs)


class Search(ReferenceMixin, base.Search):
    form = forms.LanguageSearch


class New(ReferenceMixin, base.NewEdit):
    forms = {'referenceform': forms.Reference}

    def handle_forms(self, request, referenceform):
        return referenceform.save()


class Edit(ReferenceMixin, base.NewEdit):
    forms = {'referenceform': forms.Reference}

    def handle_forms(self, request, reference, referenceform):
        return referenceform.save()


class Delete(ReferenceMixin, base.Delete):
    pass
