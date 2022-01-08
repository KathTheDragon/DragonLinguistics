from django.urls import include, path, register_converter as register
from .base import ID
from ..views import words

class Lemma(ID):
    regex = f'{ID.regex}|[^/@][^/]*'

register(Lemma, 'lemma')


app_name = 'words'
urlpatterns = [
    path('', words.List.as_view(), name='list'),
    path('search', words.Search.as_view(), name='search'),
    path('new/', words.New.as_view(), name='new'),
    path('word/<lemma:lemma>/', include([
        path('', words.View.as_view(), name='view'),
        path('edit/', words.Edit.as_view(), name='edit'),
        path('delete/', words.Delete.as_view(), name='delete'),
        path('<int:homonym>/', include([
            path('', words.View.as_view(), name='view-homonym'),
            path('edit/', words.Edit.as_view(), name='edit-homonym'),
            path('delete/', words.Delete.as_view(), name='delete-homonym'),
        ]))
    ]))
]
