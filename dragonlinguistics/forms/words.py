from django.forms import (
    CharField,
    ChoiceField,
    FileField,
    Textarea,
    Form,
    ModelForm,
    inlineformset_factory
)

from .. import models

class Word(ModelForm):
    class Meta:
        model = models.Word
        exclude = ['dictionary']
        widgets = {'notes': Textarea()}


Variants = inlineformset_factory(
    models.Word,
    models.Variant,
    exclude=['word'],
    widgets={'defin': Textarea(), 'notes': Textarea()},
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
