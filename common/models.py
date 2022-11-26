from collections.abc import Iterator

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.safestring import SafeString
from django_hosts.resolvers import reverse

class BaseModel(models.Model):
    objects: models.Manager
    DoesNotExist: type[ObjectDoesNotExist]
    id: int

    def get_absolute_url(self) -> str:
        return self.url()

    def url(self) -> str:
        raise NotImplementedError

    def get_classes(self) -> list[str]:
        return []

    def get_string(self) -> str:
        return str(self)

    def html(self) -> SafeString:
        from django.utils.html import format_html
        classes = ' '.join(self.get_classes())
        if classes:
            return format_html('<span class="{}">{}</span>', classes, self.get_string())
        else:
            return format_html('{}', self.get_string())

    class Meta:
        abstract = True


class Host:
    def __init__(self, name: str, title: str) -> None:
        self.name = name
        self.title = title

    def __str__(self) -> str:
        return self.title

    @staticmethod
    def get(name: str = 'www') -> 'Host':
        title = {
            'www': 'Home',
            'conlang': 'Conlanging',
            'hist': 'Historical Linguistics',
        }.get(name, 'Other')
        return Host(name, title)

    def url(self) -> str:
        return reverse('home', host=self.name)

    def breadcrumbs(self) -> Iterator[tuple[str, str]]:
        if self.name != 'www':
            yield from Host.get().breadcrumbs()
        yield self.url(), str(self)
