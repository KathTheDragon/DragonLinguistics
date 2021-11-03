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
        # path('grammar/<path:path>', langs.Grammar.as_view(), name='grammar'),
        # path('lessons/<slug:name>', langs.Lessons.as_view(), name='lessons'),
        # path('texts/<path:path>', langs.Texts.as_view(), name='texts'),
        path('dictionary/', include('dragonlinguistics.urls.words'))
    ]))
]
