from django import forms

from .. import models

class Reference(forms.ModelForm):
    class Meta:
        model = models.Reference
        fields = '__all__'
        widgets = {'link': forms.TextInput()}


class Search(forms.Form):
    author = forms.CharField(required=False, max_length=255)
    year = forms.IntegerField(required=False, min_value=0, max_value=32767)
    title = forms.CharField(required=False, max_length=255)
