from datetime import datetime
from django.forms import DateTimeField, ModelForm, TextInput

from .. import models

class Folder(ModelForm):
    class Meta:
        model = models.Folder
        fields = '__all__'


class NewArticle(ModelForm):
    created = DateTimeField(initial=datetime.now)

    class Meta:
        model = models.Article
        fields = ['title', 'description', 'number', 'content', 'tags', 'created']
        widgets = {'tags': TextInput()}


class EditArticle(ModelForm):
    class Meta:
        model = models.Article
        fields = ['title', 'description', 'number', 'content', 'tags']
        widgets = {'tags': TextInput()}
