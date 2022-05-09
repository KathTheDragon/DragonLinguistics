from django.urls import include, path, register_converter as register
from .base import ID
from ..views import words

class Lemma(ID):
    regex = f'{ID.regex}|[^/@][^/]*'

register(Lemma, 'lemma')


app_name = 'words'
urlpatterns = [
    path('', words.List.as_view(), name='list'),  # Includes new, search, and import
    path('<lemma:lemma>/', include([
        path('', words.View.as_view(), name='view'),  # Includes edit and delete
        path('<int:homonym>/', include([
            path('', words.View.as_view(), name='view-homonym'),  # Includes edit and delete
        ]))
    ])),
]
