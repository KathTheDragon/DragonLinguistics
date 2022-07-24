from django.urls import include, path
from . import views

def make_urlpatterns(article_folder=''):
    return [
        path('', views.ListArticles.as_view(article_folder=article_folder), name='list-articles'),
        path('<slug:slug>/', views.ViewArticle.as_view(article_folder=article_folder), name='view-article'),
    ]
