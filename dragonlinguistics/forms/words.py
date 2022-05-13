from django import forms

from .. import models

class Dictionary(forms.ModelForm):
    class Meta:
        model = models.Dictionary
        fields = '__all__'
        widgets = {
            'language': forms.HiddenInput()
        }


class Word(forms.ModelForm):
    isunattested = forms.BooleanField(required=False, label='Unattested', label_suffix='?')

    class Meta:
        model = models.Word
        fields = '__all__'
        widgets = {
            'dictionary': forms.HiddenInput()
        }


Variants = forms.inlineformset_factory(
    models.Word,
    models.Variant,
    fields = '__all__',
    widgets = {
        'word': forms.HiddenInput()
    },
    extra=1
)


Search = type('Search', (forms.Form,), {
    'lemma': forms.CharField(required=False, max_length=50),
    'type': forms.ChoiceField(required=False, choices=[('','Any'), *models.Word.TYPES]),
    'class': forms.CharField(required=False, label='Class', max_length=20),
    'definition': forms.CharField(required=False, max_length=50),
})


class Import(forms.Form):
    file = forms.FileField()
    delimiter = forms.CharField(min_length=1, max_length=1)
    quotechar = forms.CharField(min_length=1, max_length=1, label='Quote Character')
    action = forms.ChoiceField(choices=[('append', 'Append'), ('replace', 'Replace')])
