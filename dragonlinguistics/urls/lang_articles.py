from django.urls import include, path
from ..views import lang_articles

app_name = 'articles'
urlpatterns = [
    path('', lang_articles.List.as_view(), name='list'),
    path('new', lang_articles.New.as_view(), name='new'),
    path('<slug:slug>/', include([
        path('', lang_articles.View.as_view(), name='view'),
        path('edit', lang_articles.Edit.as_view(), name='edit'),
        path('delete', lang_articles.Delete.as_view(), name='delete'),
    ])),
]
