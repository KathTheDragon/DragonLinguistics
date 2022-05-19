from django.contrib import admin

from . import models

@admin.register(models.Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('author', 'year', 'title')
    list_filter = ('author',)
    search_fields = ('author', 'year', 'title')
    save_on_top = True
