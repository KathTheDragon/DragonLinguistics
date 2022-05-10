from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import ModelForm, Textarea

from . import models


admin.site.register(models.Folder)


@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'folder')
    save_on_top = True


admin.site.register(models.Language)
admin.site.register(models.User, UserAdmin)

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
    list_display = ('__str__', 'definition', lambda word: str(word.dictionary.language))
    list_filter = ('dictionary__language__name',)
    search_fields = ('lemma',)
    inlines = (VariantInline,)
    form = WordForm
    save_on_top = True


@admin.register(models.Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('author', 'year', 'title')
    list_filter = ('author',)
    search_fields = ('author', 'year', 'title')
    save_on_top = True
