from django.urls import reverse
from django.utils.text import slugify
from articles.models import Article
from languages.models import Language
from dictionaries.models import Word
from common.shortcuts import get
from markup import nodes
from markup.nodes import html, Attributes, MarkupError, InvalidData
from markup.utils import partition, strip

class LinkNode(nodes.LinkNode):
    params = nodes.LinkNode.params | {'*=': None}

    def make_data(self, data: Attributes) -> Attributes:
        if not (data['url'].startswith('#') or '.' in data['url']):
            kwargs = {key: value for key, value in data.items() if key not in nodes.LinkNode.params}
            name = data['url']
            if '#' in name:
                name, section = name.split('#')
            else:
                section = ''
            url = reverse(name, kwargs=kwargs)
            if section:
                url = f'{url}#{section}'
            data['url'] = url
        return data


class SectionNode(nodes.SectionNode):
    params = {'not-numbered?': False, 'title': None}

    @staticmethod
    def parse_data(data: Attributes, kwargs: Attributes) -> tuple[Attributes, Attributes]:
        data['number'] = kwargs.get('section_number', '1')
        parts = data['number'].split('.')
        parts[-1] = str(int(parts[-1]) + 1)
        kwargs['section_number'] = '.'.join(parts)
        return data, kwargs | {'section_number': data['number'] + '.1'}

    def make_data(self, data: Attributes) -> Attributes:
        data['level'] = str(min(6, data['number'].count('.') + 1))
        data['id'] = self.attributes['id'] or f'sect-{slugify(data["title"])}'
        return super().make_data(data)

    def make_attributes(self) -> Attributes:
        return self.attributes | {'id': self.data['id']}

    def make_content(self, text: list[str]) -> list[str]:
        number = self.data['number'].lstrip('.')
        back_to_top = html('a', {'class': ['back-to-top'], 'href': '#top'}, ['↑'])
        if not self.data['not-numbered']:
            section_num = html('a', {'class': ['section-num'], 'href': f'#{self.data["id"]}'}, [number])
            heading = [section_num, self.data['title'], back_to_top]
        else:
            heading = [self.data['title'], back_to_top]
        return super().make_content([*heading, '/', *text])


class FootnoteNode(nodes.Node):
    tag = 'p'
    params = {'number': None}

    def make_attributes(self) -> Attributes:
        return self.attributes | {'class': [*self.attributes['class'], 'footnote']}

    def make_content(self, text: list[str]) -> list[str]:
        prefix = html('sup', {}, [self.data['number']])
        return [prefix, *text]


class IpaNode(nodes.Node):
    tag = 'span'

    def make_attributes(self) -> Attributes:
        return self.attributes | {'class': [*self.attributes['class'], 'ipa']}

    def make_content(self, text: list[str]) -> list[str]:
        return [word.replace('-', '‿') for word in text]


class WordNode(nodes.Node):
    tag = 'span'
    params = {'code': ''}

    def make_attributes(self) -> Attributes:
        return self.attributes | {'class': [*self.attributes['class'], 'word', self.data['code']]}


class GlossNode(nodes.Node):
    tag = 'span'

    def make_attributes(self) -> Attributes:
        return self.attributes | {'class': [*self.attributes['class'], 'gloss']}


class QuoteNode(nodes.Node):
    tag = 'span'

    def make_attributes(self) -> Attributes:
        return self.attributes | {'class': [*self.attributes['class'], 'quote']}


class Object(nodes.Node):
    tag = 'a'
    name = ''

    def make_attributes(self) -> Attributes:
        return self.attributes | {'href': self.data[self.name].url()}

    def make_content(self, text: list[str]) -> list[str]:
        return text or [str(self.data[self.name])]


class LangObject(Object):
    params = {'code': None}
    name = 'lang'

    def make_data(self, data: Attributes) -> Attributes:
        try:
            data['lang'] = Language.objects.get(code=data['code'])
        except Language.DoesNotExist:
            raise InvalidData(f'language {data["code"]!r} does not exist')
        return data

    def make_attributes(self) -> Attributes:
        return super().make_attributes() | {'class': [*self.attributes['class'], 'lang', self.data['code']]}

    def make_content(self, text: list[str]) -> list[str]:
        return text or [str(self.data['lang'])]


class WordObject(Object):
    params = {'code': None, 'lemma': None, 'homonym': '0'}
    name = 'word'

    def make_data(self, data: Attributes) -> Attributes:
        try:
            language = Language.objects.get(code=data['code'])
        except Language.DoesNotExist:
            raise InvalidData(f'language {data["code"]!r} does not exist')

        try:
            data['word'] = get(
                Word, dictionary__language=language, lemma=data['lemma'], index=int(data['homonym']) or None)
        except Word.DoesNotExist:
            raise InvalidData(f'word {data["lemma"]!r} does not exist in language {data["code"]!r}')

        return data

    def _make_word(self, word: list[str]) -> str:
        word = word or [str(self.data['word'])]
        return html('span', {'class': ['word', self.data['code']]}, word)

    def _make_gloss(self, gloss: list[str]) -> str:
        gloss = gloss or [self.data['word'].definition()]
        return f'"{"".join(gloss)}"'

    def make_content(self, text: list[str]) -> list[str]:
        return [self._make_word(text)]


class WordGlossObject(WordObject):
    def make_content(self, text: list[str]) -> list[str]:
        parts = partition(text, '|')
        word = self._make_word(parts.pop(0) if parts else [])
        gloss = self._make_gloss(parts.pop(0) if parts else [])
        if parts:
            raise MarkupError('Could not parse text')
        return [word, ' ', gloss]


class GlossObject(WordObject):
    def make_content(self, text: list[str]) -> list[str]:
        return [self._make_gloss(text)]


class ArticleObject(Object):
    params = {'title': None, 'section': ''}
    name = 'article'

    def make_data(self, data: Attributes) -> Attributes:
        try:
            data['article'] = Article.objects.get(folder__path=data.get('path', ''), slug=slugify(data['title']))
        except Article.DoesNotExist:
            raise InvalidData(f'article {data["title"]!r} at path {data.get("path", "")!r} does not exist')
        return data

    def make_attributes(self) -> Attributes:
        attributes = super().make_attributes()
        if self.data['section']:
            attributes['href'] += f'#sect-{slugify(self.data["section"])}'
        return attributes

    def make_content(self, text: list[str]) -> list[str]:
        return text or [self.data['section'] or self.data['title']]


class LangArticleObject(ArticleObject):
    params = {'code': None} | ArticleObject.params
    type = 'articles'

    def make_data(self, data: Attributes) -> Attributes:
        try:
            lang = Language.objects.get(code=data['code'])
        except Language.DoesNotExist:
            raise InvalidData(f'language {data["code"]!r} does not exist')

        data['path'] = lang.get_folders()[self.type]
        return super().make_data(data)


class GrammarObject(LangArticleObject):
    type = 'grammar'


class LessonObject(LangArticleObject):
    type = 'lessons'


class TextObject(LangArticleObject):
    type = 'texts'


nodes = {
    'link': LinkNode,
    'section': SectionNode,
    'footnote': FootnoteNode,
    'ipa': IpaNode,
    'word': WordNode,
    'gloss': GlossNode,
    'quote': QuoteNode,
}

objects = {
    'lang': LangObject,
    'word': WordObject,
    'word-gloss': WordGlossObject,
    'gloss': GlossObject,
    'article': ArticleObject,
    'grammar': GrammarObject,
    'lesson': LessonObject,
    'text': TextObject,
}
