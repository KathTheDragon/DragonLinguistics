from django.forms import (
    CharField,
    ChoiceField,
    Textarea,
    Form,
    ModelForm,
    inlineformset_factory
)

from ..models import words as models

class Word(ModelForm):
    class Meta:
        model = models.Word
        fields = ['lemma', 'type', 'notes', 'etymology']
        widgets = {'notes': Textarea()}


Senses = inlineformset_factory(
    models.Word,
    models.Sense,
    fields=['gloss', 'defin', 'pos', 'grammclass', 'notes'],
    widgets={'defin': Textarea(), 'notes': Textarea()},
    extra=1
)


class Search(Form):
    lemma = CharField(required=False, max_length=50)
    type = ChoiceField(required=False, choices=[('','Any'), *models.Word.TYPES])
    gloss = CharField(required=False, max_length=20)
    pos = ChoiceField(required=False, choices=[('','Any'), *models.Sense.POS])
    classes = CharField(required=False, label='Class', max_length=20)
