from django import forms

from . import models

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
    'type': forms.ChoiceField(required=False, choices=[('','Any'), *models.Word.TYPES]),
    'class': forms.CharField(required=False, label='Class', max_length=20),
    'definition': forms.CharField(required=False, max_length=50),
})


class Import(forms.Form):
    file = forms.FileField()
    delimiter = forms.CharField(min_length=1, max_length=1)
    quotechar = forms.CharField(min_length=1, max_length=1, label='Quote Character')
    action = forms.ChoiceField(choices=[('append', 'Append'), ('replace', 'Replace')])
