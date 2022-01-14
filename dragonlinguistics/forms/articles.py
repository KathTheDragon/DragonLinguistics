from django.forms import ModelForm, TextInput

from .. import models

class Folder(ModelForm):
    class Meta:
        model = models.Folder
        fields = '__all__'


class Article(ModelForm):
    class Meta:
        model = models.Article
        fields = ['title', 'description', 'content', 'tags']
        widgets = {'tags': TextInput()}
