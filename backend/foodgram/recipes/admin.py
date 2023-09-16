from django.contrib import admin
from .models import Tag, Ingredient, Recipe, IngredientRecipes

# Register your models here.
class TagAdmin(admin.ModelAdmin):
    """ Модель администратора для тега """
    list_display = ('id', 'name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    """Модель администратора для ингредиентов"""
    list_display = ('id', 'name', 'measurement_unit')


class RecipeAdmin(admin.ModelAdmin):
    """ Модель администратора для рецептов"""
    list_display = ('id', 'name', 'text', 'cooking_time')


class IngredientRecipesAdmin(admin.ModelAdmin):
    """Модель администратора для ингредиентов в рецептах"""
    list_display = ('id', 'ingredients', 'recipes', 'amount')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipes, IngredientRecipesAdmin)