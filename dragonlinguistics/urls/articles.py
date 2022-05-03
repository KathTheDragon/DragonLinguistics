from django.urls import include, path
from ..views import articles

app_name = 'articles'
urlpatterns = [
    path('', articles.List.as_view(), name='list'),  # Includes new
    path('<slug:slug>/', include([
        path('', articles.View.as_view(), name='view'),  # Includes edit and delete
    ])),
]
