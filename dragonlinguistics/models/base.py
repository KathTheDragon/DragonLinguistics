from django.db import models

class Model(models.Model):
    def get_absolute_url(self):
        return self.url()

    class Meta:
        abstract = True
