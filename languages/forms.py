from django import forms

from . import models

class NewLanguage(forms.ModelForm):
    code = forms.CharField(max_length=5, min_length=3)
    class Meta:
        model = models.Language
        exclude = ['type']
        widgets = {'blurb': forms.Textarea()}
EditLanguage = NewLanguage


class Search(forms.Form):
    name = forms.CharField(required=False, max_length=50)
    code = forms.CharField(required=False, max_length=5, min_length=3)
