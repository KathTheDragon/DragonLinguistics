from django import forms

from .models import Family

class NewFamily(forms.ModelForm):
    tree = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = Family
        exclude = ['type']
        widgets = {'blurb': forms.Textarea()}
EditFamily = NewFamily
