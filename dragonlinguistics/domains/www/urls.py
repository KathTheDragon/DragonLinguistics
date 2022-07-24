from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Static pages
    path('', views.Home.as_view(), name='home'),
]
