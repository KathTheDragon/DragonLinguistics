from common import views as base
from common.shortcuts import get_object_or_404
from languages.views import get_language_type
from .forms import NewFamily, EditFamily
from .models import Clade, Family

def process_family_kwargs(view, name):
    return {'family': get_object_or_404(Family, name=name, type=get_language_type(view))}


class ListFamilies(base.Actions):
    template_folder = 'families'

    class List(base.List):
        instance = 'family'

        def get_object_list(self, **kwargs):
            return Family.objects.filter(type=get_language_type(self))

        def get_context_data(self, **kwargs):
            return super().get_context_data(**kwargs) | {'title': 'Families'}

    class New(base.New):
        form = NewFamily
        instance = 'family'

        def get_extra_attrs(self, **kwargs):
            return {'type': get_language_type(self)}

        def handle_forms(self, form, **kwargs):
            family = super().handle_forms(form=form, **kwargs)
            family.parse_clades(form.cleaned_data['tree'])
            return family


class ViewFamily(base.Actions):
    template_folder = 'families'
    process_kwargs = staticmethod(process_family_kwargs)

    class View(base.View):
        instance = 'family'

    class Edit(base.Edit):
        form = EditFamily
        instance = 'family'

        def get_forms(self, form_initial={}, **kwargs):
            tree = kwargs['family'].draw_clades(use_pipes=False)
            return super().get_forms(**kwargs, form_initial=form_initial | {'tree': tree})

        def handle_forms(self, form, **kwargs):
            family = super().handle_forms(form=form, **kwargs)
            tree = family.draw_clades(use_pipes=False)
            if form.cleaned_data['tree'].replace('\r\n', '\n') != tree:
                family.root.delete()
                family.parse_clades(form.cleaned_data['tree'])
            return family

    class Delete(base.Delete):
        instance = 'family'
