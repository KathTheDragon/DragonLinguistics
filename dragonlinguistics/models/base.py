from django.db import models

class Model(models.Model):
    def get_absolute_url(self):
        return self.url()

    def get_classes(self):
        return []

    def html(self):
        from django.utils.html import format_html
        classes = ''.join(self.get_classes())
        if classes:
            return format_html('<span class="{}">{}</span>', classes, self)
        else:
            return format_html('{}', self)

    class Meta:
        abstract = True
