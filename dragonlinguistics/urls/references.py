from django.urls import include, path, register_converter as register
from ..views import references

class Char:
    regex = '[a-z]'

    def to_python(self, value):
        return ord(value) - ord('a')

    def to_url(self, value):
        return chr(value + ord('a'))

register(Char, 'char')


app_name = 'references'
urlpatterns = [
    path('', references.List.as_view(), name='list'),  # Includes new and search
    path('<author>-<int:year><char:index>/', references.View.as_view(), name='view'),  # Includes edit and delete
]
