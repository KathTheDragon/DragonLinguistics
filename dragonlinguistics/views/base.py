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
class SearchMixin(ContextMixin):
    page_length = 100
    form = None

    def get_form(self):
        if self.form is None:
            raise ValueError
        return self.form

    def get_object_list(self, query, **kwargs):
        return []

    def get_context_data(self, **kwargs):
        from django.core.paginator import Paginator, InvalidPage
        query = self.request.GET.copy()
        objectlist = self.get_object_list(query, **kwargs)
        pages = Paginator(objectlist, self.page_length)
        try:
            page = pages.page(query.get('page', 1))
        except InvalidPage:
            raise Http404
        if 'page' in query:
            del query['page']
        searchform = self.get_form()(query)
        kwargs.setdefault('page', page)
        kwargs.setdefault('query', query)
        kwargs.setdefault('searchform', searchform)
        return super().get_context_data(**kwargs)


class Search(TemplateView):
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
