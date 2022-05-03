from . import base, articles, langs

# Views
class LangArticleMixin(articles.ArticleMixin, langs.LangMixin):
    parts = ['langs', 'articles']
    path_fmt = 'langs/{code}/{type}'


class List(base.Actions):
    class List(LangArticleMixin, articles.List.List):
        pass

    class New(LangArticleMixin, articles.List.New):
        pass


class View(base.Actions):
    class View(LangArticleMixin, articles.View.View):
        pass

    class Edit(LangArticleMixin, articles.View.Edit):
        pass

    class Delete(LangArticleMixin, articles.View.Delete):
        pass
