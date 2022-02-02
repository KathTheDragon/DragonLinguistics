from django.core.exceptions import ValidationError
from django.db import models

class Reference(models.Model):
    author = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField(min_length=4, max_length=4)
    title = models.CharField(max_length=255)
    link = models.TextField(blank=True)
    comment = models.CharField(max_length=255, blank=True)
