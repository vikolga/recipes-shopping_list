from django.contrib import admin
from .models import Tag, Ingredient, Recipe, IngredientRecipes, Favourite

# Register your models here.
class TagAdmin(admin.ModelAdmin):
    """ Модель администратора для тега """
    list_display = ('id', 'name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    """Модель администратора для ингредиентов"""
    list_display = ('id', 'name', 'measurement_unit')

class IngredientInline(admin.TabularInline):
    model = IngredientRecipes
    extra = 3


class RecipeAdmin(admin.ModelAdmin):
    """ Модель администратора для рецептов"""
    list_display = ('id', 'author', 'name', 'text', 'cooking_time')
    inlines = (IngredientInline,)


class FavouriteAdmin(admin.ModelAdmin):
    """Модель админа для избранных рецептов"""
    list_display = ('user', 'recipe')

admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favourite, FavouriteAdmin)
