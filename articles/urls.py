from django.urls import include, path
from .views import List, View

app_name = 'articles'
urlpatterns = [
    path('', List.as_view(), name='list'),  # Includes new
    path('<slug:slug>/', include([
        path('', View.as_view(), name='view'),  # Includes edit and delete
    ])),
]
