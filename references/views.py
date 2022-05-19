from django.shortcuts import redirect

from common import views as base
from . import forms
from .models import Reference

class ReferenceMixin:
    parts = ['references']
    folder = 'references'
    instance = 'reference'

    def get_kwargs(self, author=None, year=None, index=None, **kwargs):
        if author is None:
            return super().get_kwargs(**kwargs)
        else:
            reference = Reference.objects.filter(author=author, year=year)[index]
            return super().get_kwargs(reference=reference, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['type'] = 'reference'
        return super().get_context_data(**kwargs)

    def get_breadcrumbs(self, reference=None, **kwargs):
        from django.urls import reverse
        breadcrumbs = super().get_breadcrumbs(**kwargs)
        breadcrumbs.append(('Bibliography', reverse('references:list')))
        if reference is not None:
            breadcrumbs.append((reference.html(), ''))
        return breadcrumbs


class List(base.Actions):
    class List(base.SearchMixin, ReferenceMixin, base.Base):
        form = forms.Search
        fieldname = 'author'

        def get_folder(self):
            return '/'.join(self.parts)

        def get_context_data(self, **kwargs):
            query = self.request.GET
            objectlist = Reference.objects.filter(
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
        form = forms.Search

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Search', ''))
            return breadcrumbs

    class New(ReferenceMixin, base.NewEdit):
        forms = {'form': forms.Reference}
        use_addmore = True

        def handle_forms(self, request, form):
            return form.save()

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('New', ''))
            return breadcrumbs


class View(base.Actions):
    class View(ReferenceMixin, base.View):
        def get(self, request, **kwargs):
            return redirect('references:list')

    class Edit(ReferenceMixin, base.NewEdit):
        forms = {'form': forms.Reference}

        def handle_forms(self, request, form, **kwargs):
            return form.save()

        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Edit', ''))
            return breadcrumbs

    class Delete(ReferenceMixin, base.Delete):
        def get_breadcrumbs(self, **kwargs):
            breadcrumbs = super().get_breadcrumbs(**kwargs)
            breadcrumbs.append(('Delete', ''))
            return breadcrumbs
