from django.contrib import admin
from django.urls import include, path, register_converter as register
from .. import converters

register(converters.StrOrID, 'id')  # I hope I can get away with only doing it here

urlpatterns = [
    path('admin/', admin.site.urls),
    path('articles/', include('dragonlinguistics.urls.articles')),
    path('languages/', include('dragonlinguistics.urls.langs')),
    path('', include('dragonlinguistics.urls.static')),
]
