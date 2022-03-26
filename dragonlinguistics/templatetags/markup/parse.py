import string
from .html import html
from .formats import process as process_format
from .objects import process as process_object

def parse(value):
    output = ''
    while value:
        chunk, value = parse_chunk(value)
        output += chunk
    return output


CONTROL_CHARS = '@$'

def parse_chunk(value, *, exclude=''):
    if value[0] in CONTROL_CHARS:
        return parse_tag(value)
    else:
        return parse_string(value, alphabet='', exclude=exclude+CONTROL_CHARS, escape=True)


def parse_tag(value):
    # @-, $cmd#id.class.class[data]{text}
    control, value = value[0], value[1:]

    command, value = parse_string(value, error_msg='Invalid command name')

    if value and value[0] == '#':
        id, value = parse_string(value, start=1, error_msg='Invalid id')
    else:
        id = None

    classes = []
    while value and value[0] == '.':
        class_, value = parse_string(value, start=1, error_msg='Invalid class')
        classes.append(class_)

    data = []
    if value and value[0] == '[':
        value = value[1:]
        while value[0] != ']':
            if value[0] == ' ':
                value = value[1:]
                continue
            elif value[0] == '"':
                arg, value = parse_string(value, start=1, alphabet='', exclude='\r\n]"', escape=True, no_escape='\r\n')
                if value[0] != '"':
                    return error('Incomplete string'), value
                value = value[1:]
            else:
                arg, value = parse_string(value, alphabet='', exclude='\r\n]" ', escape=True, no_escape='\r\n', error_msg='Incomplete tag data')
            data.append(arg)
        value = value[1:]

    if value and value[0] == '{':
        value = value[1:]
        text = ''
        while value[0] != '}':
            chunk, value = parse_chunk(value, exclude='}')
            text += chunk
        value = value[1:]
    else:
        text = None

    if control == '@':
        func = process_object
    else:
        func = process_format
    try:
        return html(*func(command, id, classes, data, text)), value
    except MarkupError as e:
        return error(e.message), value
    except Exception:
        return error('An unknown error occurred'), value


STRING_CHARS = string.ascii_letters + string.digits + '_-'

def parse_string(value, *, start=0, alphabet=STRING_CHARS, exclude='', escape=False, no_escape='', error_msg=''):
    i = start
    while i < len(value):
        if escape and value[i] == '\\':
            if i >= len(value) - 1:
                return error('Incomplete escape sequence'), value
            elif value[i+1] in no_escape:
                return error('Invalid escape sequence'), value
            else:
                i += 2
        elif (not alphabet or value[i] in alphabet) and value[i] not in exclude:
            i += 1
        else:
            break
    if i != start:
        return value[start:i], value[i:]
    else:
        return error(error_msg), value


def error(msg):
    return f'<span class="error">&lt;{msg}&gt;</span>'
