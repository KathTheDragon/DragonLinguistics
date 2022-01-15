from . import articles, langs

# Views
class LangArticleMixin(articles.ArticleMixin, langs.LangMixin):
    folder = 'langs/articles'
    path_fmt = 'langs/{code}/{type}'


class List(LangArticleMixin, articles.List):
    pass


class New(LangArticleMixin, articles.New):
    pass


class View(LangArticleMixin, articles.View):
    pass


class Edit(LangArticleMixin, articles.Edit):
    pass


class Delete(LangArticleMixin, articles.Delete):
    pass
