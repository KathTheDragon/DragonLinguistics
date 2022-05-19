from django import forms

from . import models

class Language(forms.ModelForm):
    code = forms.CharField(max_length=5, min_length=3)
    class Meta:
        model = models.Language
        fields = ['name', 'code', 'blurb']
        widgets = {'blurb': forms.Textarea()}


class Search(forms.Form):
    name = forms.CharField(required=False, max_length=50)
    code = forms.CharField(required=False, max_length=5, min_length=3)
