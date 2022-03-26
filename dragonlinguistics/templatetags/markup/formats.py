import re
from django.urls import reverse
from .exceptions import MarkupError
from .html import html

def handle_word(command, id, classes, data, text):
    if data:
        raise MarkupError('Invalid tag data')
    classes.append('word')

    return 'span', {}, id, classes, text


def handle_tag(command, id, classes, data, text):
    if data:
        raise MarkupError('Invalid tag data')

    return command, {}, id, classes, text


def handle_link(command, id, classes, data, text):
    attributes = {}
    if data[0] == '_blank':
        attributes['target'] = data.pop(0)
    if data[0].startswith('#') or '.' in data[0]:  # In-page or external url
        url, = data
    else:  # Internal url
        name, *args = data
        if '#' in name:
            name, section = name.split('#')
        else:
            section = ''
        url = reverse(name, kwargs=dict(map(lambda s: s.split('='), args)))
        if section:
            url = f'{url}#{section}'
    attributes['href'] = url
    if text is None:
        text = url

    return 'a', attributes, id, classes, text


def handle_td(command, id, classes, data, text):
    attributes = {}
    for attr in data:
        if attr.startswith('cols='):
            attributes['colspan'] = attr.removeprefix('cols=')
        elif attr.startswith('rows='):
            attributes['rowspan'] = attr.removeprefix('rows=')
        else:
            raise MarkupError('Invalid tag data')

    return 'td', attributes, id, classes, text


def handle_section(command, id, classes, data, text):
    level, title = data

    if id is None:
        id = f'sect-{title.lower().replace(" ", "-")}'

    if level not in ('1', '2', '3', '4', '5', '6'):
        raise MarkupError('Invalid level')
    heading = html(f'h{level}', {}, title)
    if text.startswith('\n'):
        indent = re.match(r'\n( *)', text).group(1)
        text = f'\n{indent}{heading}\n{text}'
    else:
        text = f'{heading}{text}'

    return 'section', {}, id, classes, text


def handle_footnote(command, id, classes, data, text):
    number, = data
    classes.append('footnote')
    prefix = html('sup', {}, number)
    text = f'{prefix}{text}'

    return 'p', {}, id, classes, text


SIMPLE_TAGS = [
    'br', 'dl', 'dt', 'dd', 'div', 'em', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'table', 'tr', 'th', 'blockquote', 'sup', 'sub', 'strong', 'caption',
]
HANDLERS = {
    'word': handle_word_format,
    'link': handle_link,
    'td': handle_td,
    'section': handle_section,
    'footnote': handle_footnote,
}

def process(command, id, classes, data, text):
    if command in HANDLERS:
        func = HANDLERS[command]
    elif command in SIMPLE_TAGS:
        func = handle_tag
    else:
        raise MarkupError('Invalid command')

    tag, attributes, id, classes, text = func(command, id, classes, data, text)

    if id is not None:
        attributes['id'] = id
    if classes:
        attributes['class'] = ' '.join(classes)

    return tag, attributes, text
