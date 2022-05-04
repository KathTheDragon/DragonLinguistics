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

    def get_breadcrumbs(self, reference=None, **kwargs):
        from django.urls import reverse
        breadcrumbs = super().get_breadcrumbs(**kwargs)
        breadcrumbs.append(('Bibliography', reverse('references:list')))
        if reference is not None:
            breadcrumbs.append((reference.html(), ''))
        return breadcrumbs


class List(base.Actions):
    class List(base.SearchMixin, ReferenceMixin, base.Base):
        form = forms.ReferenceSearch

        def get_context_data(self, **kwargs):
            query = self.request.GET
            objectlist = models.Reference.objects.filter(
                **base.fuzzysearch(title=query.get('title', '')),
                **base.strictsearch(
                    author__istartswith=query.get('author', ''),
                    year=int(query.get('year', '0'))
                ),
            )
            authors = objectlist.values_list('author').distinct()
            author_references = {}
            for (author,) in authors:
                author_references[author] = objectlist.filter(author=author)
            kwargs['author_references'] = author_references
            return super().get_context_data(**kwargs)

    class Search(ReferenceMixin, base.Search):
        form = forms.LanguageSearch

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Search', ''))
            return breadcrumbs

    class New(ReferenceMixin, base.NewEdit):
        forms = {'referenceform': forms.Reference}

        def handle_forms(self, request, referenceform):
            return referenceform.save()

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('New', ''))
            return breadcrumbs


class View(base.Actions):
    class View(ReferenceMixin, base.Base):
        def get(self, request, **kwargs):
            return redirect('references:list')

    class Edit(ReferenceMixin, base.NewEdit):
        forms = {'referenceform': forms.Reference}

        def handle_forms(self, request, reference, referenceform):
            return referenceform.save()

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Edit', ''))
            return breadcrumbs

    class Delete(ReferenceMixin, base.Delete):
        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Delete', ''))
            return breadcrumbs
