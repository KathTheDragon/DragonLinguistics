from django.contrib import admin
from django.forms import ModelForm, Textarea

from . import models

textarea_attrs = {'rows':5, 'cols':40}

class DictionaryForm(ModelForm):
    class Meta:
        model = models.Dictionary
        exclude = ('order',)
        widgets = {
            'classes': Textarea(attrs=textarea_attrs),
        }


@admin.register(models.Dictionary)
class DictionaryAdmin(admin.ModelAdmin):
    list_display = ('language', 'classes')
    form = DictionaryForm
    save_on_top = True


class VariantForm(ModelForm):
    class Meta:
        model = models.Variant
        fields = '__all__'
        widgets = {
            'forms': Textarea(attrs=textarea_attrs),
            'definition': Textarea(attrs=textarea_attrs),
            'notes': Textarea(attrs=textarea_attrs),
            'derivatives': Textarea(attrs=textarea_attrs),
        }


class VariantInline(admin.StackedInline):
    model = models.Variant
    extra = 1
    form = VariantForm


class WordForm(ModelForm):
    class Meta:
        model = models.Word
        fields = '__all__'
        widgets = {
            'etymology': Textarea(attrs=textarea_attrs),
            'descendents': Textarea(attrs=textarea_attrs),
            'references': Textarea(attrs=textarea_attrs),
        }


@admin.register(models.Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_gloss', 'language_name')
    list_filter = ('dictionary__language__name',)
    search_fields = ('lemma',)
    inlines = (VariantInline,)
    form = WordForm
    save_on_top = True

    @staticmethod
    @admin.display(description='Language')
    def language_name(word):
        return str(word.dictionary.language)
