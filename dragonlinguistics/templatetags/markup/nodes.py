from django.urls import reverse
from django.utils.text import slugify
from dragonlinguistics.models import Article, Language, Word
from markup.nodes import handler, MarkupError, InvalidData

@handler
def link_node(command, attributes, data, text):
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


@handler
def word_node(command, attributes, data, text):
    attributes['class'].append('word')
    if data:
        code, = data
        attributes['class'].append(code)

    return 'span', attributes, text


node_handlers = {
    'link': link_node,
    'word': word_node,
}


def lang_object(command, attributes, data, text):
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


def word_object(command, attributes, data, text):
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
        if 'word' in command:
            parts.append(str(word))
        if 'gloss' in command:
            parts.append(f'"{word.firstgloss()}"')
        text = [' '.join(parts)]

    return url, attributes, text


def article_object(command, attributes, data, text):
    if len(data) == 2:
        title, section = data
    else:
        title, = data
        section = ''

    try:
        article = Article.objects.get(folder__path='', slug=slugify(title))
    except Article.DoesNotExist:
        raise MarkupError('Invalid article title')

    url = article.get_absolute_url()
    if section:
        url = f'{url}#sect-{slugify(section)}'
    attributes['href'] = url
    if text is None:
        text = [section or title]

    return url, attributes, text


def lang_article_object(command, attributes, data, text):
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
        raise MarkupError('Invalid language code/article title')

    url = article.get_absolute_url()
    if section:
        url = f'{url}#sect-{slugify(section)}'
    attributes['href'] = url
    if text is None:
        text = [section or title]

    return url, attributes, text


object_handlers = {
    'lang': handle_lang,
    'word': handle_word,
    'word-gloss': handle_word,
    'gloss': handle_word,
    'article': handle_article,
    'grammar': handle_lang_article,
    'lesson': handle_lang_article,
    'text': handle_lang_article,
}
