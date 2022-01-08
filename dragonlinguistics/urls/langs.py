from django.urls import include, path, register_converter as register
from .base import ID
from ..views import langs

class LangCode(ID):
    regex = f'{ID.regex}|[A-Z]{{3,5}}'

register(LangCode, 'code')


app_name = 'langs'
urlpatterns = [
    path('', langs.List.as_view(), name='list'),
    path('search', langs.Search.as_view(), name='search'),
    path('new', langs.New.as_view(), name='new'),
    path('lang/<code:code>/', include([
        path('', langs.View.as_view(), name='view'),
        path('edit/', langs.Edit.as_view(), name='edit'),
        path('delete/', langs.Delete.as_view(), name='delete'),
        path('grammar/', include('dragonlinguistics.urls.grammar')),
        path('lessons/', include('dragonlinguistics.urls.lessons')),
        path('texts/', include('dragonlinguistics.urls.texts')),
        path('dictionary/', include('dragonlinguistics.urls.words')),
    ]))
]
