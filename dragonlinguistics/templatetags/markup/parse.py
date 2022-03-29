import string
from .exceptions import MarkupError
from .html import html
from .formats import process as process_format
from .objects import process as process_object

class ParseError(Exception):
    def __init__(self, message, remainder):
        self.message = message
        self.remainder = remainder
        super().__init__(message)


def parse(value, *, skip_whitespace=False, exclude='', end='', embed=True, error_msg=''):
    parts = []
    quoted_exclude = exclude + '"'
    unquoted_exclude = exclude + end + '"' + string.whitespace
    while value and value[0] not in exclude + end:
        if value[0] in string.whitespace:
            part, value = parse_string(value, alphabet=string.whitespace, exclude=exclude, error_msg='Invalid whitespace')
            if skip_whitespace:
                continue
        elif value[0] == '"':
            part, value = parse_string(value[1:], alphabet='', exclude=quoted_exclude, escape=True, no_escape=exclude, embed=embed, error_msg='Empty or incomplete string')
            if value[0] != '"':
                raise ParseError('Incomplete string', value)
            value = value[1:]
        else:
            part, value = parse_string(value, alphabet='', exclude=unquoted_exclude, escape=True, no_escape=exclude, embed=embed)
        parts.append(part)
    return parts, value


STRING_CHARS = string.ascii_letters + string.digits + '_-'
CONTROL_CHARS = '@$'

def parse_string(value, *, alphabet=STRING_CHARS, exclude='', escape=False, no_escape='', embed=False, error_msg=''):
    out = ''
    while value:
        if escape and value[0] == '\\':
            if len(value) <= 1:
                raise ParseError('Incomplete escape sequence', value)
            elif value[1] in no_escape:
                raise ParseError('Invalid escape sequence', value)
            else:
                out += value[:2]  # Unescaping here?
                value = value[2:]
        elif embed and value[0] in CONTROL_CHARS:
            tag, value = parse_tag(value)
            out += tag
        elif (not alphabet or value[0] in alphabet) and value[0] not in exclude:
            out += value[0]
            value = value[1:]
        else:
            break
    if out:
        return out, value
    else:
        raise ParseError(error_msg, value)


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
        return parse_string(value[1:], error_msg='Invalid id')
    else:
        return None, value


def parse_classes(value):
    classes = []
    while value and value[0] == '.':
        class_, value = parse_string(value[1:], error_msg='Invalid class')
        classes.append(class_)
    return classes, value


def parse_data(value):
    if value and value[0] == '[':
        data, value = parse(value[1:], skip_whitespace=True, exclude='\r\n', end=']', embed=False)
        return data, value[1:]
    else:
        return [], value


def parse_text(value):
    if value and value[0] == '{':
        text, value = parse(value[1:], end='}')
        return text, value[1:]
    else:
        return None, value


def error(msg):
    return f'<span class="error">&lt;{msg}&gt;</span>'
