from django.urls import include, path
from ..views import lessons

app_name = 'lessons'
urlpatterns = [
    path('', lessons.List.as_view(), name='list'),
    # path('search', lessons.Search.as_view(), name='search'),
    path('new', lessons.New.as_view(), name='new'),
    path('<slug:slug>/', include([
        path('', lessons.View.as_view(), name='view'),
        path('edit', lessons.Edit.as_view(), name='edit'),
        path('delete', lessons.Delete.as_view(), name='delete'),
    ])),
]
