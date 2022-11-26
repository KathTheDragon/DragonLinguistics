from typing import Any

from django.shortcuts import redirect

from common import views as base
from common.shortcuts import get_object_or_404
from .forms import NewAuthor, EditAuthor, NewReference, EditReference
from .models import Author, Reference

def process_author_kwargs(view, name: str) -> dict[str, Any]:
    return {'author': get_object_or_404(Author, slug=name)}


def process_reference_kwargs(view, name: str, year: int, index: int) -> dict[str, Any]:
    kwargs = process_author_kwargs(view, name)
    return kwargs | {'reference': get_object_or_404(Reference, author=kwargs['author'], year=year, index=index)}


class ViewBibliography(base.Actions):
    template_folder = 'bibliography'

    class View(base.View):
        instance = 'bibliography'

        def get_context_data(self, **kwargs) -> dict[str, Any]:
            return super().get_context_data(**kwargs) | {
                'title': 'Bibliography',
                'type': 'author',
                'authors': Author.objects.all(),
            }

    # class New(base.New):
    #     form = NewAuthor
    #     instance = 'author'


class ViewAuthor(base.Actions):
    template_folder = 'bibliography'
    process_kwargs = staticmethod(process_author_kwargs)

    class View(base.View):
        instance = 'author'

        def get_context_data(self, **kwargs) -> dict[str, Any]:
            return super().get_context_data(**kwargs) | {
                'references': Reference.objects.filter(author=kwargs['author'])}

    # class Edit(base.Edit):
    #     form = EditAuthor
    #     instance = 'author'

    # class Delete(base.Delete):
    #     instance = 'author'

    # class New(base.New):
    #     form = NewReference
    #     instance = 'reference'
    #     parent = 'author'


class ViewReference(base.Actions):
    template_folder = 'bibliography'
    process_kwargs = staticmethod(process_reference_kwargs)

    class View(base.View):
        instance = 'reference'

    # class Edit(base.Edit):
    #     form = EditReference
    #     instance = 'reference'

    # class Delete(base.Delete):
    #     instance = 'reference'
