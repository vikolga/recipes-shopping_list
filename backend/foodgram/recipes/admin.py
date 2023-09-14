from django.contrib import admin
from .models import Tag

# Register your models here.
class TagAdmin(admin.ModelAdmin):
    """ Модель администратора для тега """
    list_display = ('id', 'name', 'color', 'slug')


admin.site.register(Tag, TagAdmin)