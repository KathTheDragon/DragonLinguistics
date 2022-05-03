from django.urls import include, path, register_converter as register
from .base import ID
from ..views import langs

class LangCode(ID):
    regex = f'{ID.regex}|[A-Z]{{3,5}}'


class ArticleType:
    regex = 'articles|grammar|lessons|texts'

    def to_python(self, value): return value

    def to_url(self, value): return value


register(LangCode, 'code')
register(ArticleType, 'type')

app_name = 'langs'
urlpatterns = [
    path('', langs.List.as_view(), name='list'),  # Includes new and search
    path('<code:code>/', include([
        path('', langs.View.as_view(), name='view'),  # Includes edit and delete
        path('<type:type>/', include('dragonlinguistics.urls.lang_articles')),
        path('dictionary/', include('dragonlinguistics.urls.words')),
    ]))
]
