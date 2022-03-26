from django.utils.text import slugify
from dragonlinguistics.models import Article, Language, Word
from .exceptions import MarkupError

def handle_lang(command, id, classes, data, text):
    code, = data
    try:
        lang = Language.objects.get(code=code)
    except Language.DoesNotExist:
        raise MarkupError('Invalid language code')

    url = lang.get_absolute_url()
    classes.extend(['lang', code])
    if text is None:
        text = str(lang)

    return url, id, classes, text


def handle_word(command, id, classes, data, text):
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

    url = word.get_absolute_url()
    classes.extend(['word', code])
    if text is None:
        if command == 'word':
            text = str(word)
        elif command == 'word-gloss':
            text = f'{word} "{word.firstgloss()}"'
        else:
            text = f'"{word.firstgloss()}"'

    return url, id, classes, text


def handle_article(command, id, classes, data, text):
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
    if text is None:
        text = section or title

    return url, id, classes, text


def handle_lang_article(command, id, classes, data, text):
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
    if text is None:
        text = section or title

    return url, id, classes, text


HANDLERS = {
    'lang': handle_lang,
    'word': handle_word,
    'word-gloss': handle_word,
    'gloss': handle_word,
    'article': handle_article,
    'grammar': handle_lang_article,
    'lesson': handle_lang_article,
    'text': handle_lang_article,
}

def process(command, id, classes, data, text):
    if command in HANDLERS:
        func = HANDLERS[command]
    else:
        raise MarkupError('Invalid command')

    url, id, classes, text = func(command, id, classes, data, text)

    attributes = {'href': url}
    if id is not None:
        attributes['id'] = id
    if classes:
        attributes['class'] = ' '.join(classes)

    return 'a', attributes, text
