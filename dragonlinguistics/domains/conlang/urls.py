from django.urls import include, path
from . import views

import articles.urls
import languages.urls

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('articles/', include(articles.urls.make_urlpatterns(article_folder='conlangs/'))),
    path('languages/', include(languages.urls.urlpatterns)),
]
