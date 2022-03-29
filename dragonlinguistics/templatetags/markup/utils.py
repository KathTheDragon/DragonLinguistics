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
