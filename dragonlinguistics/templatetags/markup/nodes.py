from django.urls import reverse
from django.utils.text import slugify
from dragonlinguistics.models import Article, Language, Word
from markup import nodes
from markup.nodes import handler, html, MarkupError, InvalidData

@handler
def link_node(attributes, data, text):
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
        text = [url]

    return 'a', attributes, text


def section_node(id, classes, data, text):
    if len(data) != 2:
        raise InvalidData()
    else:
        number, title = data

    if id is None:
        id = f'sect-{slugify(title)}'
    level = str(number.count('.') + 1)
    number = number.lstrip('0.')
    if number:
        section_num = html('a', {'class': ['section-num'], 'href': f'#{id}'}, [number])
    else:
        section_num = ''
    back_to_top = html('a', {'class': ['back-to-top'], 'href': '#top'}, ['↑'])
    title = f'{section_num} {title} {back_to_top}'

    return nodes.section_node(id, classes, [level, title], text)


@handler
def ipa_node(attributes, data, text):
    if data:
        raise InvalidData()
    attributes['class'].append('ipa')
    text = [word.replace(' ', chr(0xA0)) for word in text]

    return 'span', attributes, text


@handler
def word_node(attributes, data, text):
    attributes['class'].append('word')
    if data:
        code, = data
        attributes['class'].append(code)

    return 'span', attributes, text


node_handlers = {
    'link': link_node,
    'section': section_node,
    'ipa': ipa_node,
    'word': word_node,
}


@handler
def lang_object(attributes, data, text):
    code, = data
    try:
        lang = Language.objects.get(code=code)
    except Language.DoesNotExist:
        raise MarkupError('Invalid language code')

    attributes['href'] = lang.get_absolute_url()
    attributes['class'].extend(['lang', code])
    if text is None:
        text = [str(lang)]

    return 'a', attributes, text


def _make_word_object(node):
    @handler
    def word_object(attributes, data, text):
        if len(data) == 2:
            code, lemma = data
            homonym = 0
        else:
            code, lemma, homonym = data

        try:
            lang = Language.objects.get(code=code)
        except Language.DoesNotExist:
            raise MarkupError('Invalid language code')

        try:
            word = Word.objects.get(lang=lang, lemma=lemma, homonym=homonym)
        except Word.DoesNotExist:
            raise MarkupError('Invalid lemma/homonym number')

        attributes['href'] = word.get_absolute_url()
        attributes['class'].extend(['word', code])
        if text is None:
            parts = []
            if 'word' in node:
                parts.append(str(word))
            if 'gloss' in node:
                parts.append(f'"{word.firstgloss()}"')
            text = [' '.join(parts)]

        return 'a', attributes, text
    name = f'{node}_object'
    word_object.__name__ = name
    word_object.__qualname__ = name

    return word_object


def _article_object(attributes, text, path, title, section=''):
    try:
        article = Article.objects.get(folder__path=path, slug=slugify(title))
    except Article.DoesNotExist:
        raise MarkupError('Invalid article title')

    url = article.get_absolute_url()
    if section:
        url = f'{url}#sect-{slugify(section)}'
    attributes['href'] = url
    if text is None:
        text = [section or title]

    return 'a', attributes, text


@handler
def article_object(attributes, data, text):
    return _article_object(attributes, text, '', *data)


def _make_lang_article_object(type):
    name = f'{type}_object'
    if type != 'grammar':
        type += 's'

    @handler
    def lang_article_object(attributes, data, text):
        code = data.pop(0)
        return _article_object(attributes, text, f'langs/{code}/{type}', *data)
    lang_article_object.__name__ = name
    lang_article_object.__qualname__ = name

    return lang_article_object


object_handlers = {
    'lang': lang_object,
    'word': _make_word_object('word'),
    'word-gloss': _make_word_object('word-gloss'),
    'gloss': _make_word_object('gloss'),
    'article': article_object,
    'grammar': _make_lang_article_object('grammar'),
    'lesson': _make_lang_article_object('lesson'),
    'text': _make_lang_article_object('text'),
}
