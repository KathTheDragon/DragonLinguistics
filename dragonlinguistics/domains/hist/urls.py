from django.urls import include, path
from . import views

import articles.urls
import languages.urls
import references.urls

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('articles/', include(articles.urls.make_urlpatterns(article_folder='natlangs/')), kwargs={'citeable': True}),
    path('bibliography/', include(references.urls.urlpatterns)),
    path('languages/', include(languages.urls.urlpatterns), kwargs={'type': 'natlang'}),
]
