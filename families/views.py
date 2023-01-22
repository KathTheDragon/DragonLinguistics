from typing import Any

from common import views as base
from common.shortcuts import get_object_or_404
from languages.views import get_language_type
from .models import Family

def process_family_kwargs(view, name: str) -> dict[str, Any]:
    return {'family': get_object_or_404(Family, name=name, type=get_language_type(view))}


class ListFamilies(base.Actions):
    template_folder = 'families'

    class List(base.List):
        instance = 'family'

        def get_object_list(self, **kwargs):
            return Family.objects.filter(type=get_language_type(self))

        def get_context_data(self, **kwargs) -> dict[str, Any]:
            return super().get_context_data(**kwargs) | {'title': 'Families'}

class ViewFamily(base.Actions):
    template_folder = 'families'
    process_kwargs = staticmethod(process_family_kwargs)

    class View(base.View):
        instance = 'family'
