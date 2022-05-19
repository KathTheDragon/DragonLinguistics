from django.contrib import admin

from . import models

admin.site.register(models.Folder)

@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'folder')
    save_on_top = True
