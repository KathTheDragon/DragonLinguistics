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
        exclude = ['lang']
        widgets = {'notes': Textarea()}


Senses = inlineformset_factory(
    models.Word,
    models.Sense,
    exclude=['word'],
    widgets={'defin': Textarea(), 'notes': Textarea()},
    extra=1
)


class Search(Form):
    lemma = CharField(required=False, max_length=50)
    type = ChoiceField(required=False, choices=[('','Any'), *models.Word.TYPES])
    gloss = CharField(required=False, max_length=20)
    pos = ChoiceField(required=False, choices=[('','Any'), *models.Sense.POS])
    classes = CharField(required=False, label='Class', max_length=20)


class Import(Form):
    file = FileField()
    delimiter = CharField(min_length=1, max_length=1)
    quotechar = CharField(min_length=1, max_length=1, label='Quote Character')
    action = ChoiceField(choices=[('append', 'Append'), ('replace', 'Replace')])
