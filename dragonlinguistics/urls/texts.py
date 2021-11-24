from django.urls import include, path
from ..views import texts

app_name = 'texts'
urlpatterns = [
    path('', texts.List.as_view(), name='list'),
    # path('search', texts.Search.as_view(), name='search'),
    path('new', texts.New.as_view(), name='new'),
    path('<slug:slug>/', include([
        path('', texts.View.as_view(), name='view'),
        path('edit', texts.Edit.as_view(), name='edit'),
        path('delete', texts.Delete.as_view(), name='delete'),
    ])),
]
