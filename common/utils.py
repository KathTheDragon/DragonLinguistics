def get(model, *args, index=None, **kwargs):
    if index is None:
        return model.objects.get(*args, **kwargs)
    else:
        try:
            return list(model.objects.filter(*args, **kwargs))[index]
        except IndexError:
            raise model.DoesNotExist
