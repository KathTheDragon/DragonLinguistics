from django.urls import reverse
from django.utils.text import slugify
from dragonlinguistics.models import Article, Language, Word
from markup import nodes
from markup.nodes import html, Attributes, MarkupError, InvalidData

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
    params = {'number': None, 'title': None}

    def make_data(self, data: Attributes) -> Attributes:
        number, title = data['number'], data['title']
        data['level'] = str(number.count('.') + 1)
        data['id'] = id = self.attributes['id'] or f'sect-{slugify(title)}'
        number = number.lstrip('0.')
        if number:
            section_num = html('a', {'class': ['section-num'], 'href': f'#{id}'}, [number])
        else:
            section_num = ''
        back_to_top = html('a', {'class': ['back-to-top'], 'href': '#top'}, ['↑'])
        data['title'] = f'{section_num} {title} {back_to_top}'
        return super().make_data(data)

    def make_attributes(self) -> Attributes:
        return self.attributes | {'id': self.data['id']}


class FootnoteNode(nodes.Node):
    tag = 'p'
    params = {'number': None}

    def make_attributes(self) -> Attributes:
        return self.attributes | {'class': [*self.attributes['class'], 'footnote']}

    def make_content(self) -> list[str]:
        prefix = html('sup', {}, [self.data['number']])
        return [prefix, *(self.text or [])]


class IpaNode(nodes.Node):
    tag = 'span'

    def make_attributes(self) -> Attributes:
        return self.attributes | {'class': [*self.attributes['class'], 'ipa']}

    def make_content(self) -> list[str]:
        return [word.replace(' ', chr(0xA0)) for word in (self.text or [])]


class WordNode(nodes.Node):
    tag = 'span'
    params = {'code': ''}

    def make_attributes(self) -> Attributes:
        return self.attributes | {'class': [*self.attributes['class'], 'word', self.data['code']]}


class Object(nodes.Node):
    tag = 'a'
    name = ''

    def make_attributes(self) -> Attributes:
        return self.attributes | {'href': self.data[self.name].get_absolute_url()}

    def make_content(self) -> list[str]:
        return self.text or [str(self.data[self.name])]


class LangObject(nodes.Node):
    params = {'code': None}
    name = 'lang'

    def parse_data(self, data: Attributes) -> Attributes:
        try:
            data['lang'] = Language.objects.get(code=data['code'])
        except Language.DoesNotExist:
            raise InvalidData(f'language {data["code"]!r} does not exist')
        return data

    def make_attributes(self) -> Attributes:
        return super().make_attributes() | {'class': [*self.attributes['class'], 'lang', self.data['code']]}

    def make_content(self) -> list[str]:
        return self.text or [str(self.data['lang'])]


class WordObject(nodes.Node):
    params = {'code': None, 'lemma': None, 'homonym': '0'}
    name = 'word'

    def make_data(self, data: Attributes) -> Attributes:
        try:
            lang = Language.objects.get(code=data['code'])
        except Language.DoesNotExist:
            raise InvalidData(f'language {data["code"]!r} does not exist')

        try:
            data['word'] = Word.objects.get(lang=lang, lemma=data['lemma'], homonym=int(data['homonym']))
        except Word.DoesNotExist:
            raise InvalidData(f'word {data["lemma"]!r} does not exist in language {data["code"]!r}')

        return data

    def _make_word(self, word: list[str]) -> str:
        word = word or [str(self.data['word'])]
        return html('span', {'class': ['word', self.data['code']]}, word)

    def _make_gloss(self, gloss: list[str]) -> str:
        gloss = gloss or [self.data['word'].firstgloss()]
        return f'"{"".join(gloss)}"'

    def make_content(self) -> list[str]:
        return [self._make_word(self.text)]


class WordGlossObject(WordObject):
    def make_content(self) -> list[str]:
        parts = [strip(part)[1] for part in partition(self.text, '|')]
        word = self._make_word(parts.pop(0) if parts else [])
        gloss = self._make_gloss(parts.pop(0) if parts else [])
        if parts:
            raise MarkupError('Could not parse text')
        return [word, ' ', gloss]


class GlossObject(WordObject):
    def make_content(self) -> list[str]:
        return [self._make_gloss(self.text)]


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

    def make_content(self) -> list[str]:
        return self.text or [self.data['section'] or self.data['title']]


class LangArticleObject(ArticleObject):
    params = {'code': None} | ArticleObject.params
    type = ''

    def make_data(self, data: Attributes) -> Attributes:
        data['path'] = f'langs/{data["code"]}/{self.type}'
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
