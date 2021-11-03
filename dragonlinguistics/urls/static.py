from django.urls import path
from ..views import static

urlpatterns = [
    path('', static.Home.as_view(), name='home'),
]
