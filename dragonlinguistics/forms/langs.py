from django.forms import CharField, Textarea, Form, ModelForm

from ..models import langs as models

class Language(ModelForm):
    code = CharField(max_length=5, min_length=3)
    class Meta:
        model = models.Language
        fields = ['name', 'code', 'hasgrammar', 'blurb']
        widgets = {'blurb': Textarea()}


class Search(Form):
    name = CharField(required=False, max_length=50)
    code = CharField(required=False, max_length=5, min_length=3)
