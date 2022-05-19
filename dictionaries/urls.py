from django.urls import include, path, register_converter as register
from common.url_converters import ID
from .views import List, View

class Lemma(ID):
    regex = f'{ID.regex}|[^/@][^/]*'

register(Lemma, 'lemma')


app_name = 'words'
urlpatterns = [
    path('', List.as_view(), name='list'),  # Includes new, search, and import
    path('<lemma:lemma>/', include([
        path('', View.as_view(), name='view'),  # Includes edit and delete
        path('<int:homonym>/', include([
            path('', View.as_view(), name='view-homonym'),  # Includes edit and delete
        ]))
    ])),
]
