from django.urls import include, path
from ..views import words

app_name = 'words'
urlpatterns = [
    path('', words.ListWords.as_view(), name='list'),
    path('search', words.SearchWords.as_view(), name='search'),
    path('new/', words.NewWord.as_view(), name='new'),
    path('word/<id:lemma>/', include([
        path('', words.ViewWord.as_view(), name='view'),
        path('edit/', words.EditWord.as_view(), name='edit'),
        path('delete/', words.DeleteWord.as_view(), name='delete'),
        path('<int:homonym>/', include([
            path('', words.ViewWord.as_view(), name='view-homonym'),
            path('edit/', words.EditWord.as_view(), name='edit-homonym'),
            path('delete/', words.DeleteWord.as_view(), name='delete-homonym'),
        ]))
    ]))
]
