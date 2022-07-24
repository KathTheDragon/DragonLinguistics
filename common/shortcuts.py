from django.http import Http404
from django.shortcuts import get_object_or_404 as base_get_object_or_404

def get_object_or_404(model, *args, index=None, **kwargs):
    if index is None:
        return base_get_object_or_404(model, *args, **kwargs)
    else:
        try:
            return list(model.objects.filter(*args, **kwargs))[index]
        except IndexError:
            raise Http404
