from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('articles/', include('dragonlinguistics.urls.articles')),
    path('languages/', include('dragonlinguistics.urls.langs')),
    path('', include('dragonlinguistics.urls.static')),
]


class ID:
    regex = r'@\d{1,9}'

    def to_python(self, value):
        if value.startswith('@'):
            return int(value.removeprefix('@'))
        else:
            return value

    def to_url(self, value):
        if isinstance(value, int):
            return f'@{value}'
        elif isinstance(value, str):
            return value
        else:
            raise ValueError
