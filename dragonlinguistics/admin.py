from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import ModelForm, Textarea

from .models.langs import Language
from .models.user import User
from .models.words import Word, Sense


admin.site.register(Language)
admin.site.register(User, UserAdmin)

textarea_attrs = {'rows':5, 'cols':40}

class SenseForm(ModelForm):
    class Meta:
        model = Sense
        fields = '__all__'
        widgets = {
            'defin': Textarea(attrs=textarea_attrs),
            'notes': Textarea(attrs=textarea_attrs),
        }


class SenseInline(admin.StackedInline):
    model = Sense
    extra = 1
    form = SenseForm


class WordForm(ModelForm):
    class Meta:
        model = Word
        fields = '__all__'
        widgets = {
            'notes': Textarea(attrs=textarea_attrs),
        }


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'firstgloss', 'lang')
    list_filter = ('lang__name',)
    search_fields = ('lemma',)
    fields = ('lang', 'lemma', 'homonym', 'type', 'notes')
    inlines = (SenseInline,)
    form = WordForm
    save_on_top = True
