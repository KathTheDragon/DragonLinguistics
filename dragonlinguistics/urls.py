from django.contrib import admin
from django.urls import include, path

from .views import Home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('articles/', include('articles.urls')),
    path('bibliography/', include('references.urls')),
    path('languages/', include('languages.urls')),
    # Static pages
    path('', Home.as_view(), name='home'),
]
