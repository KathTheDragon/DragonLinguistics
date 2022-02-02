import re, string
from html import escape
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.urls import reverse
from django.utils.text import slugify
from django.utils.safestring import mark_safe

from ..models import Article, Language, Word

register = Library()

@register.filter(needs_autoescape=True)
@stringfilter
def markup(value, autoescape=True):
    if autoescape:
        value = conditional_escape(value, quote=False)
    output = ''
    while value:
        chunk, value = parse_chunk(value)
        output += chunk
    return mark_safe(output)


# Reimplement conditional_escape to be able to not escape quotes
def conditional_escape(text, quote=True):
    if hasattr(text, '__html__'):
        return text.__html__()
    else:
        return mark_safe(escape(str(text), quote=quote))


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
        return process_link(command, id, classes, data, text), value
    else:
        return process_format(command, id, classes, data, text), value


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


def process_link(command, id, classes, data, text):
    attributes = {}

    if command == 'lang':
        code, = data
        try:
            lang = Language.objects.get(code=code)
        except Language.DoesNotExist:
            return error('Invalid language code')

        url = lang.get_absolute_url()
        classes.extend(['lang', code])
        if text is None:
            text = str(lang)
    elif command in ('word', 'word-gloss', 'gloss'):
        if len(data) == 2:
            code, lemma = data
            homonym = 0
        else:
            code, lemma, homonym = data

        try:
            lang = Language.objects.get(code=code)
        except Language.DoesNotExist:
            return error('Invalid language code')

        try:
            word = Word.objects.get(lang=lang, lemma=lemma, homonym=homonym)
        except Word.DoesNotExist:
            return error('Invalid lemma/homonym number')

        url = word.get_absolute_url()
        classes.extend(['word', code])
        if text is None:
            if command == 'word':
                text = str(word)
            elif command == 'word-gloss':
                text = f'{word} "{word.firstgloss()}"'
            else:
                text = f'"{word.firstgloss()}"'
    elif command == 'article':
        if len(data) == 2:
            title, section = data
        else:
            title, = data
            section = ''

        try:
            article = Article.objects.get(folder__path='', slug=slugify(title))
        except Article.DoesNotExist:
            return error('Invalid article title')

        url = article.get_absolute_url()
        if section:
            url = f'{url}#sect-{slugify(section)}'
        if text is None:
            text = section or title
    elif command in ('grammar', 'lesson', 'text'):
        if command != 'grammar':
            command += 's'

        if len(data) == 3:
            code, title, section = data
        else:
            code, title = data
            section = ''

        try:
            article = Article.objects.get(folder__path=f'langs/{code}/{command}', slug=slugify(title))
        except Article.DoesNotExist:
            return error('Invalid language code/article title')

        url = article.get_absolute_url()
        if section:
            url = f'{url}#sect-{slugify(section)}'
        if text is None:
            text = section or title
    else:
        return error('Invalid command')

    attributes['href'] = url
    if id is not None:
        attributes['id'] = id
    if classes:
        attributes['class'] = ' '.join(classes)

    return html('a', attributes, text)


SIMPLE_TAGS = [
    'br', 'dl', 'dt', 'dd', 'div', 'em', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'table', 'tr', 'th', 'blockquote', 'sup', 'sub',
]

def process_format(command, id, classes, data, text):
    attributes = {}

    if command == 'word':
        if data:
            return error('Invalid tag data')
        command = 'span'
        classes.append('word')
    elif command in SIMPLE_TAGS:
        if data:
            return error('Invalid tag data')
    elif command == 'link':
        command = 'a'
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
    elif command == 'td':
        for attr in data:
            if attr.startswith('cols='):
                attributes['colspan'] = attr.removeprefix('cols=')
            elif attr.startswith('rows='):
                attributes['rowspan'] = attr.removeprefix('rows=')
            else:
                return error('Invalid tag data')
    elif command == 'section':
        level, title = data

        if id is None:
            id = f'sect-{title.lower().replace(" ", "-")}'

        if level not in ('1', '2', '3', '4', '5', '6'):
            return error('Invalid level')
        heading = html(f'h{level}', {}, title)
        if text.startswith('\n'):
            indent = re.match(r'\n( *)', text).group(1)
            text = f'\n{indent}{heading}\n{text}'
        else:
            text = f'{heading}{text}'
    elif command == 'footnote':
        command = 'p'
        number, = data
        classes.append('footnote')
        prefix = html('sup', {}, '1')
        text = f'{prefix}{text}'
    else:
        return error('Invalid command')

    if id is not None:
        attributes['id'] = id
    if classes:
        attributes['class'] = ' '.join(classes)

    return html(command, attributes, text)


def html(tag, attributes={}, content=None):
    if attributes:
        open = f'{tag} {format_attributes(attributes)}'
    else:
        open = tag
    close = tag

    if content is None:  # Self-closing
        return f'<{open} />'
    else:
        return f'<{open}>{content}</{close}>'


def format_attributes(attributes):
    attrs = []
    for attribute, value in attributes.items():
        if value is True:
            attrs.append(attribute)
        elif value:
            attrs.append(f'{attribute}="{value}"')
    return ' '.join(attrs)


def error(msg):
    return f'<span class="error">&lt;{msg}&gt;</span>'
