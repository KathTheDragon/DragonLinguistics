from django.urls import include, path

import articles.views
import dictionaries.urls
from . import views

def make_article_urlpatterns(type='articles', article_folder=''):
    return [
        path('', articles.views.ListArticles.as_view(
            process_kwargs=views.process_lang_folder_kwargs, template_folder=type,
            article_folder=article_folder), name=f'list-{type}'),
        path('<slug:slug>', articles.views.ViewArticle.as_view(
            process_kwargs=views.process_lang_article_kwargs, template_folder=type,
            article_folder=article_folder), name=f'view-{type.removesuffix("s")}'),
    ]


urlpatterns = [
    path('', views.ListLanguages.as_view(), name='list-languages'),
    path('<str:name>/', include([
        path('', views.ViewLanguage.as_view(), name='view-language'),
        path('articles/', include(make_article_urlpatterns(type='lang-articles', article_folder='{language.type}s/{language.code}/'))),
        path('grammar/', include(make_article_urlpatterns(type='grammar', article_folder='{language.type}s/{language.code}/grammar/'))),
        path('lessons/', include(make_article_urlpatterns(type='lessons', article_folder='{language.type}s/{language.code}/lessons/'))),
        path('texts/', include(make_article_urlpatterns(type='texts', article_folder='{language.type}s/{language.code}/texts/'))),
        path('dictionary/', include(dictionaries.urls.urlpatterns)),
    ])),
]
