from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('articles/', include('articles.urls')),
    path('bibliography/', include('references.urls')),
    path('languages/', include('languages.urls')),
    path('', include('dragonlinguistics.urls.static')),
]
