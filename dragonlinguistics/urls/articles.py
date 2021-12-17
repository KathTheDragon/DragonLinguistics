from django.urls import include, path
from ..views import articles

app_name = 'articles'
urlpatterns = [
    path('', articles.List.as_view(), name='list'),
    # path('search', articles.Search.as_view(), name='search'),
    path('new', articles.New.as_view(), name='new'),
    path('<slug:slug>/', include([
        path('', articles.View.as_view(), name='view'),
        path('edit', articles.Edit.as_view(), name='edit'),
        path('delete', articles.Delete.as_view(), name='delete'),
    ])),
]
