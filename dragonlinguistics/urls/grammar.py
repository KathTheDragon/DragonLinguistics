from django.urls import include, path
from ..views import grammar

app_name = 'grammar'
urlpatterns = [
    path('', grammar.List.as_view(), name='list'),
    # path('search', grammar.Search.as_view(), name='search'),
    path('new', grammar.New.as_view(), name='new'),
    path('<slug:slug>/', include([
        path('', grammar.View.as_view(), name='view'),
        path('edit', grammar.Edit.as_view(), name='edit'),
        path('delete', grammar.Delete.as_view(), name='delete'),
    ])),
]
