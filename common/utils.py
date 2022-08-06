def get(model, *args, index=None, **kwargs):
    if index is None:
        return model.objects.get(*args, **kwargs)
    else:
        try:
            return list(model.objects.filter(*args, **kwargs))[index]
        except IndexError:
            raise model.DoesNotExist


def pluralise(string: str) -> str:
    if string.endswith('y'):
        string = string.removesuffix('y') + 'ies'
    elif string.endswith('s') or string.endswith('x') or string.endswith('z'):
        string += 'es'
    else:
        string += 's'
    return string
