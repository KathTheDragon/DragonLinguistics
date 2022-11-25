import csv

from django import forms
from django.core.exceptions import ValidationError

from . import models
from .utils import parse_csv

class EditDictionary(forms.ModelForm):
    class Meta:
        model = models.Dictionary
        exclude = ['language']


class NewWord(forms.ModelForm):
    isunattested = forms.BooleanField(required=False, label='Unattested', label_suffix='?')

    class Meta:
        model = models.Word
        exclude = ['dictionary']
        widgets = {
            'references': forms.TextInput(),
        }
EditWord = NewWord


def make_etymology_form(dictionary):
    class Etymology(forms.Form):
        kind = forms.ChoiceField(required=False, choices=dictionary.get_derivation_options())
        components = forms.CharField(required=False)
        notes = forms.CharField(required=False, widget=forms.TextInput)

        prefix = 'etymology'

    return Etymology


def make_variants_formset(dictionary):
    class Variant(forms.ModelForm):
        lexclass = forms.ChoiceField(label='Class', choices=dictionary.get_class_options())

        class Meta:
            model = models.Variant
            exclude = ['word']
            widgets = {
                'forms': forms.TextInput(),
            }

    return forms.inlineformset_factory(
        models.Word,
        models.Variant,
        form=Variant,
        min_num=1,
        extra=0,
    )


Search = type('Search', (forms.Form,), {
    'lemma': forms.CharField(required=False, max_length=50),
    'type': forms.ChoiceField(required=False, choices=[('', 'Any'), *models.Variant.TYPES]),
    'class': forms.CharField(required=False, label='Class', max_length=20),
    'definition': forms.CharField(required=False, max_length=50),
})


class ImportDictionary(forms.Form):
    file = forms.FileField()
    delimiter = forms.CharField(min_length=1, max_length=1, initial=',')
    quotechar = forms.CharField(min_length=1, max_length=1, initial='"', label='Quote Character')
    action = forms.ChoiceField(choices=[('append', 'Append'), ('replace', 'Replace')])

    def clean(self):
        cleaned_data = super().clean().copy()
        file = cleaned_data.pop('file', None)
        delimiter = cleaned_data.pop('delimiter', None)
        quotechar = cleaned_data.pop('quotechar', None)

        if file and delimiter and quotechar:
            try:
                entries = parse_csv(file, delimiter, quotechar)
            except csv.Error as e:
                raise ValidationError(f'Could not parse the file: {e}') from None
            return cleaned_data | {'entries': entries}


class ExportDictionary(forms.Form):
    delimiter = forms.CharField(min_length=1, max_length=1, initial=',')
    quotechar = forms.CharField(min_length=1, max_length=1, initial='"', label='Quote Character')
