from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('articles/', include('dragonlinguistics.urls.articles')),
    path('bibliography/', include('dragonlinguistics.urls.references')),
    path('languages/', include('dragonlinguistics.urls.langs')),
    path('', include('dragonlinguistics.urls.static')),
]
