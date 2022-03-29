def partition(strings, separator):
    parts = []
    i = 0
    while i < len(strings):
        if strings[i] == separator:
            parts.append(strings[:i])
            strings = strings[i+1:]
        else:
            i += 1
    parts.append(strings)
    return parts


def strip(strings):
    leading = trailing = ''
    if strings[0].isspace():
        leading = strings.pop(0)
    if strings[-1].isspace():
        trailing = strings.pop()
    return leading, strings, trailing
