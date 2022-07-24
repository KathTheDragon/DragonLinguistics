from django import forms

from . import models

class NewAuthor(forms.ModelForm):
    class Meta:
        model = models.Author
        exclude = ['slug', 'alphabetise']
EditAuthor = NewAuthor


class NewReference(forms.ModelForm):
    class Meta:
        model = models.Reference
        exclude = ['author']
        widgets = {'link': forms.TextInput()}
EditReference = NewReference


class Search(forms.Form):
    author = forms.CharField(required=False, max_length=255)
    year = forms.IntegerField(required=False, min_value=0, max_value=32767)
    title = forms.CharField(required=False, max_length=255)
