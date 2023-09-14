from django.contrib import admin
from .models import Tag, Ingredient

# Register your models here.
class TagAdmin(admin.ModelAdmin):
    """ Модель администратора для тега """
    list_display = ('id', 'name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    """Модель администратора для ингредиентов"""
    list_display = ('id', 'name', 'measurement_unit')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)