from django.forms import (
    BooleanField,
    CharField,
    ChoiceField,
    FileField,
    Textarea,
    Form,
    ModelForm,
    inlineformset_factory
)

from .. import models

class Dictionary(ModelForm):
    class Meta:
        model = models.Dictionary
        exclude = ['language']


class Word(ModelForm):
    isunattested = BooleanField(required=False, label='Unattested', label_suffix='?')

    class Meta:
        model = models.Word
        exclude = ['dictionary']


Variants = inlineformset_factory(
    models.Word,
    models.Variant,
    exclude=['word'],
    extra=1
)


Search = type('Search', (Form,), {
    'lemma': CharField(required=False, max_length=50),
    'type': ChoiceField(required=False, choices=[('','Any'), *models.Word.TYPES]),
    'class': CharField(required=False, label='Class', max_length=20),
    'definition': CharField(required=False, max_length=50),
})


class Import(Form):
    file = FileField()
    delimiter = CharField(min_length=1, max_length=1)
    quotechar = CharField(min_length=1, max_length=1, label='Quote Character')
    action = ChoiceField(choices=[('append', 'Append'), ('replace', 'Replace')])
