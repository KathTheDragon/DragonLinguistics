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


class List(base.SearchMixin, ReferenceMixin, base.List):
    form = forms.ReferenceSearch

    def get_object_list(self, **kwargs):
        query = self.request.GET
        return models.Reference.objects.filter(
            **base.fuzzysearch(author=query.get('author', ''), title=query.get('title', '')),
            **base.strictsearch(year=int(query.get('year', '0'))),
        )


class Search(ReferenceMixin, base.Search):
    target_url = 'references:list'
    form = forms.LanguageSearch


class New(ReferenceMixin, base.NewEdit):
    forms = {'referenceform': (forms.Reference, 'reference')}

    def handle_forms(self, request, referenceform):
        reference = referenceform.save()
        return redirect('references:list')


class Edit(ReferenceMixin, base.NewEdit):
    forms = {'referenceform': (forms.Reference, 'reference')}

    def handle_forms(self, request, referenceform):
        reference = referenceform.save()
        return redirect('references:list')


class Delete(ReferenceMixin, base.SecureBase):
    def post(self, request, reference):
        reference.delete()
        return redirect('references:list')