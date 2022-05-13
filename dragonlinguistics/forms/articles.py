from datetime import datetime
from django import forms

from .. import models

class Folder(forms.ModelForm):
    class Meta:
        model = models.Folder
        fields = '__all__'


class NewArticle(forms.ModelForm):
    created = forms.DateTimeField(initial=datetime.now)

    class Meta:
        model = models.Article
        exclude = ['slug', 'edited']
        widgets = {
            'folder': forms.HiddenInput(),
            'tags': forms.TextInput(),
        }


class EditArticle(forms.ModelForm):
    class Meta:
        model = models.Article
        exclude = ['slug', 'created', 'edited']
        widgets = {
            'folder': forms.HiddenInput(),
            'tags': forms.TextInput(),
        }
