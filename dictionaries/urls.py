from django.urls import include, path, register_converter as register
from common.url_converters import ID
from . import views

urlpatterns = [
    path('', views.ViewDictionary.as_view(), name='view-dictionary'),
    path('<str:lemma>/', views.ViewWord.as_view(), name='view-word'),
]
