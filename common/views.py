from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import Http404
from django.shortcuts import redirect
from django.views import generic
from django.views.generic.base import ContextMixin

from .models import Host

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

    def get_default_action(self):
        return next(name for name, value in vars(type(self)).items() if is_action(value))

    def get_template_folder(self):
        return self.template_folder

    def get_action_attrs(self):
        return {'template_folder': self.get_template_folder()}

    @staticmethod
    def process_kwargs(self, **kwargs):
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
            raise Http404


class Base(generic.TemplateView):
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {'host': Host.get(self.request.host.name)}


class Action(Base):
    template_folder = ''
    template_name = ''
    instance = ''

    def get_template_name(self):
        return self.template_name.format(instance=self.instance)

    def get_template_names(self):
        return [f'{self.template_folder}/{self.get_template_name()}.html'.lstrip('/')]

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {'object': kwargs.get(self.instance)}


class SecureAction(LoginRequiredMixin, Action):
    pass


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
        return super().get_context_data(**kwargs) | {'page': page}


class List(PageMixin, Action):
    template_name = 'list-{instance}s'


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


class NewEdit(SecureAction):
    form = None
    formset = None
    redirects = {
        '_edit': '{obj.url()}?edit',
        '_view': '{obj.url()}',
        '_list': '{obj.list_url()}',
    }

    def get_form_class(self, **kwargs):
        if self.form is None:
            raise ValueError
        else:
            return self.form

    def get_formset_class(self, **kwargs):
        return self.formset or (lambda data, initial, instance: None)

    def get_forms(self, form_data=None, initial_data=None, **kwargs):
        instance = kwargs.get(self.instance)
        return (
            self.get_form_class(**kwargs)(form_data, initial=initial_data, instance=instance),
            self.get_formset_class(**kwargs)(form_data, initial=initial_data, instance=instance)
        )

    def get_context_data(self, **kwargs):
        form, formset = self.get_forms(**kwargs)
        return super().get_context_data(**kwargs) | {'form': form, 'formset': formset}

    def handle_forms(self, form, formset, **kwargs):
        raise ValueError

    def get_redirect(self, obj):
        return obj.url()

    def post(self, request, **kwargs):
        form, formset = self.get_forms(form_data=request.POST, **kwargs)
        if '_add-section' in request.POST:
            post_data = request.POST.copy()
            key = f'{formset.prefix}-TOTAL_FORMS'
            post_data[key] = str(int(post_data[key]) + 1)
            return self.get(request, **kwargs, form_data=post_data)
        elif all((f is None or f.is_valid()) for f in [form, formset]):
            obj = self.handle_forms(form, formset, **kwargs)
            for key, redirect_fmt in self.redirects.items():
                if key in request.POST:
                    return redirect(redirect_fmt.format(obj))
            else:
                raise Http404
        else:
            return self.get(request, **kwargs, form_data=request.POST)


class New(NewEdit):
    template_name = 'new-{instance}'
    parent = ''
    extra_attrs = {}
    redirects = NewEdit.redirects | {'_new': '{obj.list_url()}?new'}

    def get_extra_attrs(self, **kwargs):
        return self.extra_attrs

    def handle_forms(self, form, formset, **kwargs):
        obj = form.save(commit=False)
        if self.parent:
            setattr(obj, self.parent, kwargs.get(self.parent))
        for attr, value in self.get_extra_attrs(**kwargs).items():
            setattr(obj, attr, value)
        obj.save()
        if formset is not None:
            objs = formset.save(commit=False)
            for _obj in objs:
                setattr(_obj, self.instance, obj)
                _obj.save()
        return obj


class Edit(NewEdit):
    template_name = 'edit-{instance}'

    def handle_forms(self, form, formset, **kwargs):
        obj = form.save()
        if formset is not None:
            formset.save()
        return obj


class Delete(SecureAction):
    template_name = 'delete-{instance}'

    def post(self, request, **kwargs):
        obj = kwargs[self.instance]
        obj.delete()
        return redirect(obj.list_url())
