from pathlib import PurePath

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import Http404
from django.shortcuts import redirect
from django.views import generic
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


def redirect_params(url, kwargs=None, params=None, exclude=set()):
    from urllib.parse import urlencode
    if kwargs is None:
        kwargs = {}
    response = redirect(url, **kwargs)
    if params:
        params = {key: value for key, value in params.items() if key not in exclude and value}
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
        kwargs['page'] = page
        return super().get_context_data(**kwargs)


class SearchMixin(ContextMixin):
    page_length = 100
    form = None
    fieldname = ''

    def get_form(self):
        if self.form is None:
            raise ValueError
        return self.form

    def get_context_data(self, **kwargs):
        query = self.request.GET
        searchform = self.get_form()(query)
        kwargs['query'] = query
        kwargs['search'] = True
        kwargs['searchfield'] = searchform[self.fieldname]
        return super().get_context_data(**kwargs)


class Actions(generic.View):
    default_action = ''

    def get_default_action(self):
        return self.default_action or self.__class__.__name__.lower()

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
        if isinstance(view, type) and issubclass(view, generic.View):
            return view.as_view()(request, **kwargs)
        else:
            raise Http404


BASE_PATH = PurePath('dragonlinguistics')


class Base(generic.TemplateView):
    parts = []
    name = None
    instance = None

    def get_folder(self):
        return ''

    def get_namespace(self):
        return ':'.join(self.parts)

    def get_template_names(self):
        if self.name is not None:
            name = self.name
        else:
            name = self.__class__.__name__.lower().replace('_', '-')
        return [(BASE_PATH / self.get_folder() / name).with_suffix('.html').as_posix()]

    def get_kwargs(self, **kwargs):
        return kwargs

    def dispatch(self, request, **kwargs):
        try:
            return super().dispatch(request, **self.get_kwargs(**kwargs))
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            raise Http404

    def get_breadcrumbs(self, **kwargs):
        from django.urls import reverse
        return [('Home', reverse('home'))]

    def get_context_data(self, **kwargs):
        breadcrumbs = self.get_breadcrumbs(**kwargs)
        breadcrumbs[-1] = (breadcrumbs[-1][0], '')
        kwargs['breadcrumbs'] = breadcrumbs
        kwargs['navbar_active'] = self.parts[0] if self.parts else 'home'
        return super().get_context_data(**kwargs)


class SecureBase(LoginRequiredMixin, Base):
    pass


class List(PageMixin, Base):
    def get_folder(self):
        return ''

    def get_context_data(self, **kwargs):
        kwargs.setdefault('title', (kwargs['type'] + 's').title())
        return super().get_context_data(**kwargs)


class View(Base):
    def get_folder(self):
        return '/'.join(self.parts)


class Search(Base):
    form = None

    def get_form(self):
        if self.form is None:
            raise ValueError
        else:
            return self.form

    def get_context_data(self, **kwargs):
        kwargs['form'] = self.get_form()()
        return super().get_context_data(**kwargs)

    def get_target_url(self):
        return f'{self.get_namespace()}:list'

    def get(self, request, **kwargs):
        if list(request.GET.keys()) == ['search']:
            return super().get(request, **kwargs)
        else:
            return redirect_params(
                self.get_target_url(),
                kwargs=kwargs,
                params=request.GET,
            )


class NewEdit(SecureBase):
    forms = None  # dict[str, Form]
    extra_fields = []  # list[str]
    use_addmore = False  # bool

    def get_forms(self, **kwargs):
        if self.forms is None:
            raise ValueError
        return self.forms

    def get_context_data(self, **kwargs):
        instance = kwargs.get(self.instance)
        kwargs['object'] = instance
        for attr, form in self.get_forms(**kwargs).items():
            kwargs.setdefault(attr, form(instance=instance))
        kwargs['use_addmore'] = self.use_addmore
        return super().get_context_data(**kwargs)

    def post(self, request, **kwargs):
        instance = kwargs.get(self.instance)
        forms = {
            attr: form(request.POST, instance=instance)
            for attr, form in self.get_forms(**kwargs).items()
        }
        extra_fields = {attr: request.POST.get(attr) for attr in self.extra_fields}
        if all(form.is_valid() for form in forms.values()):
            obj = self.handle_forms(request, **kwargs, **forms, **extra_fields)
            if '_add-another' in request.POST:
                return redirect(obj.list_url() + '?new')
            elif '_keep-editing' in request.POST:
                return redirect(obj.url() + '?edit')
            elif '_save' in request.POST:
                return redirect(obj)
            else:
                raise Http404
        else:
            return self.get(request, **kwargs, **forms, **extra_fields)


class Delete(SecureBase):
    def get_context_data(self, **kwargs):
        kwargs['object'] = kwargs.get(self.instance)
        return super().get_context_data(**kwargs)

    def cleanup(self, **kwargs):
        pass

    def get_redirect_to(self, **kwargs):
        return f'{self.get_namespace()}:list'

    def get_redirect_kwargs(self, **kwargs):
        return {}

    def post(self, request, **kwargs):
        kwargs.pop(self.instance).delete()
        self.cleanup(**kwargs)
        return redirect(self.get_redirect_to(**kwargs), **self.get_redirect_kwargs(**kwargs))
