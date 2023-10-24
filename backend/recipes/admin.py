from django.contrib import admin
from .models import (Tag, Ingredient, Recipe, IngredientRecipes,
                     Favourite, TagRecipes)


class TagAdmin(admin.ModelAdmin):
    """ Модель администратора для тега """
    list_display = ('id', 'name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    """Модель администратора для ингредиентов"""
    list_display = ('id', 'name', 'measurement_unit')
    # list_filter = ('name')


class IngredientInline(admin.TabularInline):
    model = IngredientRecipes
    extra = 3
    list_filter = ('name')


class TagInline(admin.TabularInline):
    model = TagRecipes
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    """ Модель администратора для рецептов"""
    list_display = ('id', 'author', 'name', 'cooking_time', 'is_favorite')
    inlines = (IngredientInline, TagInline,)
    list_filter = ('name', 'author', 'tags')

    def is_favorite(self, obj):
        return obj.favouriting.count()

    is_favorite.short_description = 'Избранное'


class FavouriteAdmin(admin.ModelAdmin):
    """Модель админа для избранных рецептов"""
    list_display = ('user', 'recipe')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favourite, FavouriteAdmin)
