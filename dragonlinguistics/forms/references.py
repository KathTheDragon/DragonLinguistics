from django.forms import CharField, Form, IntegerField, ModelForm, TextInput

from .. import models

class Reference(ModelForm):
    class Meta:
        model = models.Reference
        fields = '__all__'
        widgets = {'link': TextInput()}


class Search(Form):
    author = CharField(required=False, max_length=255)
    year = IntegerField(required=False, min_value=0, max_value=32767)
    title = CharField(required=False, max_length=255)
