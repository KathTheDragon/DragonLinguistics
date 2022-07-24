from django.db import models
from django_hosts.resolvers import reverse

class BaseModel(models.Model):
    def get_absolute_url(self):
        return self.url()

    def get_classes(self):
        return []

    def get_string(self):
        return str(self)

    def html(self):
        from django.utils.html import format_html
        classes = ' '.join(self.get_classes())
        if classes:
            return format_html('<span class="{}">{}</span>', classes, self.get_string())
        else:
            return format_html('{}', self.get_string())

    class Meta:
        abstract = True


class Host:
    def __init__(self, name, title):
        self.name = name
        self.title = title

    def __str__(self):
        return self.title

    @staticmethod
    def get(name='www'):
        title = {
            'www': 'Home',
            'conlang': 'Conlanging',
            'hist': 'Historical Linguistics',
        }.get(name, 'Other')
        return Host(name, title)

    def url(self):
        return reverse('home', host=self.name)
