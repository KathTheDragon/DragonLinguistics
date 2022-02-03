from django.shortcuts import redirect

from . import base
from .. import forms, models

class ReferenceMixin:
    folder = 'references'

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
            **base.fuzzysearch(author=query.get('author', ''), title=query.get('title', '')),
            **base.strictsearch(year=int(query.get('year', '0'))),
        )
        authors = objectlist.values_list('author').distinct()
        author_references = {}
        for (author,) in authors:
            author_references[author] = objectlist.filter(author=author)
        kwargs.setdefault('author_references', author_references)
        return super().get_context_data(**kwargs)


class Search(ReferenceMixin, base.Search):
    target_url = 'references:list'
    form = forms.LanguageSearch


class New(ReferenceMixin, base.NewEdit):
    forms = {'referenceform': (forms.Reference, 'reference')}
    extra_fields = ['addmore']

    def handle_forms(self, request, referenceform, addmore):
        reference = referenceform.save()
        if addmore is not None:
            return self.get(request, addmore=addmore)
        else:
            return redirect('references:list')


class Edit(ReferenceMixin, base.NewEdit):
    forms = {'referenceform': (forms.Reference, 'reference')}

    def handle_forms(self, request, reference, referenceform):
        referenceform.save()
        return redirect('references:list')


class Delete(ReferenceMixin, base.SecureBase):
    def post(self, request, reference):
        reference.delete()
        return redirect('references:list')
