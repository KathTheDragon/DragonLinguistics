import string
from .exceptions import MarkupError
from .html import html
from .formats import process as process_format
from .objects import process as process_object

class ParseError(MarkupError):
    def __init__(self, message, remainder):
        self.remainder = remainder
        super().__init__(message)


def parse(value, *, end=''):
    output = ''
    while value and value[0] not in end:
        chunk, value = parse_chunk(value, exclude=end)
        output += chunk
    return output, value


CONTROL_CHARS = '@$'

def parse_chunk(value, *, exclude=''):
    try:
        if value[0] in CONTROL_CHARS:
            return parse_tag(value)
        else:
            return parse_string(value, alphabet='', exclude=exclude+CONTROL_CHARS, escape=True)
    except ParseError as e:
        return error(e.message), e.remainder


def parse_tag(value):
    # @-, $cmd#id.class.class[data]{text}
    if value[0] == '@':
        func = process_object
    else:
        func = process_format
    value = value[1:]
    command, value = parse_string(value, error_msg='Invalid command name')
    id, value = parse_id(value)
    classes, value = parse_classes(value)
    data, value = parse_data(value)
    text, value = parse_text(value)

    try:
        return html(*func(command, id, classes, data, text)), value
    except MarkupError as e:
        raise ParseError(e.message, value)
    except Exception:
        raise ParseError('An unknown error occurred', value)


def parse_id(value):
    if value and value[0] == '#':
        return parse_string(value, start=1, error_msg='Invalid id')
    else:
        return None, value


def parse_classes(value):
    classes = []
    while value and value[0] == '.':
        class_, value = parse_string(value, start=1, error_msg='Invalid class')
        classes.append(class_)
    return classes, value


def parse_data(value):
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
                    raise ParseError('Incomplete string', value)
                value = value[1:]
            else:
                arg, value = parse_string(value, alphabet='', exclude='\r\n]" ', escape=True, no_escape='\r\n', error_msg='Incomplete tag data')
            data.append(arg)
        value = value[1:]
    return data, value


def parse_text(value):
    if value and value[0] == '{':
        text, value = parse(value[1:], end='}')
        return text, value[1:]
    else:
        return None, value


STRING_CHARS = string.ascii_letters + string.digits + '_-'

def parse_string(value, *, start=0, alphabet=STRING_CHARS, exclude='', escape=False, no_escape='', error_msg=''):
    i = start
    while i < len(value):
        if escape and value[i] == '\\':
            if i >= len(value) - 1:
                raise ParseError('Incomplete escape sequence', value)
            elif value[i+1] in no_escape:
                raise ParseError('Invalid escape sequence', value)
            else:
                i += 2
        elif (not alphabet or value[i] in alphabet) and value[i] not in exclude:
            i += 1
        else:
            break
    if i != start:
        return value[start:i], value[i:]
    else:
        raise ParseError(error_msg, value)


def error(msg):
    return f'<span class="error">&lt;{msg}&gt;</span>'
