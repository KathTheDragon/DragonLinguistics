from . import base, articles, langs

# Views
class LangArticleMixin(articles.ArticleMixin, langs.LangMixin):
    parts = ['langs', 'articles']
    path_fmt = 'langs/{code}/{type}'

    def get_context_data(self, **kwargs):
        type = kwargs['type']
        kwargs['crumb'] = type.title()
        kwargs['title'] = f'{kwargs["lang"].name} {type.title()}'
        if type.endswith('s'):
            type = type.removesuffix('s')
        else:
            type = f'{type} article'
        kwargs['type'] = type
        return super().get_context_data(**kwargs)


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
