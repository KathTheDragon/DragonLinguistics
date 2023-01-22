from typing import Any

from django.http import Http404
from django.views import generic
from django.views.generic.base import ContextMixin

from .models import Host
from .utils import pluralise

# ## Helper functions
# def fuzzysearch(**kwargs):
#     params = {}
#     for term, value in kwargs.items():
#         if value == '*':
#             pass
#         elif value.startswith('*') and value.endswith('*'):
#             params[f'{term}__contains'] = value.strip('*')
#         elif value.startswith('*'):
#             params[f'{term}__endswith'] = value.strip('*')
#         elif value.endswith('*'):
#             params[f'{term}__startswith'] = value.strip('*')
#         elif value:
#             params[term] = value
#     return params
#
#
# def strictsearch(**kwargs):
#     return {term: value for term, value in kwargs.items() if value}
#
#
# def redirect_params(url, kwargs=None, params=None, exclude=set()):
#     from urllib.parse import urlencode
#     if kwargs is None:
#         kwargs = {}
#     response = redirect(url, **kwargs)
#     if params:
#         params = {key: value for key, value in params.items() if key not in exclude and value}
#     if params:
#         query_string = urlencode(params)
#         response['Location'] += '?' + query_string
#     return response


## Views
# class SearchMixin(ContextMixin):
#     page_length = 100
#     form = None
#     fieldname = ''
#
#     def get_form(self):
#         if self.form is None:
#             raise ValueError
#         return self.form
#
#     def get_context_data(self, **kwargs):
#         query = self.request.GET
#         searchform = self.get_form()(query)
#         kwargs['query'] = query
#         kwargs['search'] = True
#         kwargs['searchfield'] = searchform[self.fieldname]
#         return super().get_context_data(**kwargs)
def is_action(obj):
    return isinstance(obj, type) and issubclass(obj, Action)


class Actions(generic.View):
    template_folder = ''

    def get_default_action(self) -> str:
        return next(name for name, value in vars(type(self)).items() if is_action(value))

    def get_template_folder(self) -> str:
        return self.template_folder

    def get_action_attrs(self) -> dict[str, str]:
        return {'template_folder': self.get_template_folder()}

    @staticmethod
    def process_kwargs(self, **kwargs) -> dict[str, Any]:
        return kwargs

    def dispatch(self, request, **kwargs):
        default_action = self.get_default_action()

        if request.method.lower() == 'get':
            action, values = next(request.GET.lists(), ('', [' ']))
            if not values or values[0] != '':
                action = default_action
        elif request.method.lower() == 'post':
            action = request.POST.get('_action', default_action)
        else:
            action = default_action

        view = getattr(self, action.capitalize(), None)
        if is_action(view):
            return view.as_view(**self.get_action_attrs())(request, **self.process_kwargs(self, **kwargs))
        else:
            raise Http404(f'{action!r} is not a valid action for this page')


class Base(generic.TemplateView):
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        return super().get_context_data(**kwargs) | {'host': Host.get(self.request.host.name)}


class Action(Base):
    template_folder = ''
    template_name = ''
    instance = ''

    def get_template_name(self) -> str:
        return self.template_name.format(instance=self.instance)

    def get_template_names(self) -> list[str]:
        return [f'{self.template_folder}/{self.get_template_name()}.html'.lstrip('/')]

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        return super().get_context_data(**kwargs) | {
            'type': self.instance,
            'object': kwargs.get(self.instance),
        }


class PageMixin(ContextMixin):
    page_length = 100

    def get_object_list(self, **kwargs):
        return []

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        from django.core.paginator import Paginator, InvalidPage
        objectlist = self.get_object_list(**kwargs)
        pagenum = self.request.GET.get('page', 1)
        try:
            page = Paginator(objectlist, self.page_length).page(pagenum)
        except InvalidPage:
            raise Http404
        return super().get_context_data(**kwargs) | {'page': page}


class List(PageMixin, Action):
    template_name = 'list-{instances}'

    def get_template_name(self) -> str:
        return self.template_name.format(instances=pluralise(self.instance))


class View(Action):
    template_name = 'view-{instance}'


# class Search(Action):
#     form = None
#     target = None
#
#     def get_form(self):
#         if self.form is None:
#             raise ValueError
#         else:
#             return self.form
#
#     def get_context_data(self, **kwargs):
#         kwargs['form'] = self.get_form()()
#         return super().get_context_data(**kwargs)
#
#     def get_target_url(self):
#         if self.target is None:
#             raise ValueError
#         else:
#             return self.target
#
#     def get(self, request, **kwargs):
#         if list(request.GET.keys()) == ['search']:
#             return super().get(request, **kwargs)
#         else:
#             return redirect_params(
#                 self.get_target_url(),
#                 kwargs=kwargs,
#                 params=request.GET,
#             )
