from django.http import Http404
from common.utils import get

def get_object_or_404(model, *args, index=None, **kwargs):
    try:
        return get(model, *args, index=None, **kwargs)
    except model.DoesNotExist:
        raise Http404(f'No {model._meta.object_name} matches the given query.')
