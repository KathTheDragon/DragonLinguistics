from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import ModelForm, Textarea

from . import models


admin.site.register(models.Language)
admin.site.register(models.User, UserAdmin)

textarea_attrs = {'rows':5, 'cols':40}

class SenseForm(ModelForm):
    class Meta:
        model = models.Sense
        fields = '__all__'
        widgets = {
            'defin': Textarea(attrs=textarea_attrs),
            'notes': Textarea(attrs=textarea_attrs),
        }


class SenseInline(admin.StackedInline):
    model = models.Sense
    extra = 1
    form = SenseForm


class WordForm(ModelForm):
    class Meta:
        model = models.Word
        fields = '__all__'
        widgets = {
            'notes': Textarea(attrs=textarea_attrs),
        }


@admin.register(models.Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'firstgloss', 'lang')
    list_filter = ('lang__name',)
    search_fields = ('lemma',)
    fields = ('lang', 'lemma', 'homonym', 'type', 'notes')
    inlines = (SenseInline,)
    form = WordForm
    save_on_top = True
