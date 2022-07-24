from django.urls import include, path, register_converter as register
from . import views

class Char:
    regex = '[a-z]'

    def to_python(self, value):
        return ord(value) - ord('a')

    def to_url(self, value):
        return chr(value + ord('a'))

register(Char, 'char')

urlpatterns = [
    path('', views.ViewBibliography.as_view(), name='view-bibliography'),
    path('<str:name>/', include([
        path('', views.ViewAuthor.as_view(), name='view-author'),
        path('<int:year><char:index>/', views.ViewReference.as_view(), name='view-reference'),
    ])),
]
