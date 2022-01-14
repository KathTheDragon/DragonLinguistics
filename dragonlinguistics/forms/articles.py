from django.forms import CharField, Textarea, Form, ModelForm

from .. import models

class Folder(ModelForm):
    class Meta:
        model = models.Folder
        fields = '__all__'


class Article(ModelForm):
    class Meta:
        model = models.Article
        fields = ['title', 'description', 'content', 'tags']
