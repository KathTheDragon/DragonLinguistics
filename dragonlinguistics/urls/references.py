from django.urls import include, path, register_converter as register
from ..views import references

class Char:
    regex = '[a-z]'

    def to_python(self, value):
        return ord(value) - ord('a')

    def to_url(self, value):
        return char(value + ord('a'))

register(Char, 'char')


app_name = 'references'
urlpatterns = [
    path('', references.List.as_view(), name='list'),
    path('search', references.Search.as_view(), name='search'),
    path('new', references.New.as_view(), name='new'),
    path('<author>-<int:year><char:index>/', include([
        path('edit', references.Edit.as_view(), name='edit'),
        path('delete', references.Delete.as_view(), name='delete'),
    ])),
]
