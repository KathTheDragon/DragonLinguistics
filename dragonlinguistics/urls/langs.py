from django.urls import include, path
from ..views import langs

app_name = 'langs'
urlpatterns = [
    path('', langs.List.as_view(), name='list'),
    path('search', langs.Search.as_view(), name='search'),
    path('new', langs.New.as_view(), name='new'),
    path('lang/<id:code>/', include([
        path('', langs.View.as_view(), name='view'),
        path('edit/', langs.Edit.as_view(), name='edit'),
        path('delete/', langs.Delete.as_view(), name='delete'),
        path('grammar/', include('dragonlinguistics.urls.grammar')),
        path('lessons/', include('dragonlinguistics.urls.lessons')),
        path('texts/', include('dragonlinguistics.urls.texts')),
        path('dictionary/', include('dragonlinguistics.urls.words')),
    ]))
]
