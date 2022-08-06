from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.ListFamilies.as_view(), name='list-families'),
    path('<str:name>/', views.ViewFamily.as_view(), name='view-family'),
]
