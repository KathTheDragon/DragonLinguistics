from django.urls import include, path
from ..views import lang_articles as articles

app_name = 'lessons'
kwargs = {'folder': 'lessons', 'path': 'langs/{code}/lessons', 'namespace': 'langs:lessons'}
urlpatterns = [
    path('', articles.List.as_view(**kwargs), name='list'),
    # path('search', articles.Search.as_view(), name='search'),
    path('new', articles.New.as_view(**kwargs), name='new'),
    path('<slug:slug>/', include([
        path('', articles.View.as_view(**kwargs), name='view'),
        path('edit', articles.Edit.as_view(**kwargs), name='edit'),
        path('delete', articles.Delete.as_view(**kwargs), name='delete'),
    ])),
]
