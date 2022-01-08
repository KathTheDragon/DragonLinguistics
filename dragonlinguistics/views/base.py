from pathlib import PurePath

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.generic.base import ContextMixin

## Helper functions
def fuzzysearch(**kwargs):
    params = {}
    for term, value in kwargs.items():
        if value == '*':
            pass
        elif value.startswith('*') and value.endswith('*'):
            params[f'{term}__contains'] = value.strip('*')
        elif value.startswith('*'):
            params[f'{term}__endswith'] = value.strip('*')
        elif value.endswith('*'):
            params[f'{term}__startswith'] = value.strip('*')
        elif value:
            params[term] = value
    return params


def strictsearch(**kwargs):
    return {term: value for term, value in kwargs.items() if value}


def redirect_params(url, kwargs=None, params=None):
    from urllib.parse import urlencode
    if kwargs is None:
        kwargs = {}
    response = redirect(url, **kwargs)
    if params:
        params = {key: value for key, value in params.items() if value}
    if params:
        query_string = urlencode(params)
        response['Location'] += '?' + query_string
    return response


## Views
class PageMixin(ContextMixin):
    page_length = 100

    def get_object_list(self, **kwargs):
        return []

    def get_context_data(self, **kwargs):
        from django.core.paginator import Paginator, InvalidPage
        objectlist = self.get_object_list(**kwargs)
        pagenum = self.request.GET.get('page', 1)
        try:
            page = Paginator(objectlist, self.page_length).page(pagenum)
        except InvalidPage:
            raise Http404
        kwargs.setdefault('page', page)
        return super().get_context_data(**kwargs)


class SearchMixin(ContextMixin):
    page_length = 100
    form = None

    def get_form(self):
        if self.form is None:
            raise ValueError
        return self.form

    def get_context_data(self, **kwargs):
        query = self.request.GET
        searchform = self.get_form()(query)
        kwargs.setdefault('query', query)
        kwargs.setdefault('searchform', searchform)
        return super().get_context_data(**kwargs)


BASE_PATH = PurePath('dragonlinguistics')


class Base(TemplateView):
    folder = ''
    name = None

    def get_template_names(self):
        if self.name is not None:
            name = self.name
        else:
            name = self.__class__.__name__.lower().replace('_', '-')
        return [(BASE_PATH / self.folder / name).with_suffix('.html').as_posix()]

    def get_kwargs(self, **kwargs):
        return kwargs

    def dispatch(self, request, **kwargs):
        try:
            return super().dispatch(request, **self.get_kwargs(**kwargs))
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            raise Http404


class List(PageMixin, Base):
    pass


class Search(Base):
    target_url = None
    form = None

    def get_form(self):
        if self.form is None:
            raise ValueError
        else:
            return self.form

    def get_context_data(self, **kwargs):
        kwargs.setdefault('searchform', self.get_form()())
        return super().get_context_data(**kwargs)

    def get_target_url(self):
        if self.target_url is None:
            raise ValueError
        else:
            return self.target_url

    def get(self, request, **kwargs):
        if request.GET:
            return redirect_params(
                self.get_target_url(),
                kwargs=kwargs,
                params=request.GET
            )
        else:
            return super().get(request, **kwargs)


class NewEdit(Base):
    forms = None  # dict[str, (Form, str)]
    extra_fields = []  # list[str]

    def get_context_data(self, **kwargs):
        if self.forms is None:
            raise ValueError

        for attr, (form, instance) in self.forms.items():
            kwargs.setdefault(attr, form(instance=kwargs.get(instance)))
        return super().get_context_data(**kwargs)

    def post(self, request, **kwargs):
        if self.forms is None:
            raise ValueError

        forms = {
            attr: form(request.POST, instance=kwargs.get(instance))
            for attr, (form, instance) in self.forms.items()
        }
        extra_fields = {attr: request.POST.get(attr) for attr in self.extra_fields}
        if all(form.is_valid() for form in forms.values()):
            return self.handle_forms(request, **kwargs, **forms, **extra_fields)
        else:
            return self.get(request, **kwargs, **forms, **extra_fields)
