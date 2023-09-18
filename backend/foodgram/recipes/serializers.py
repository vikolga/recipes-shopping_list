from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (ModelSerializer,
SerializerMethodField, SlugRelatedField, ReadOnlyField)
from .models import (Tag, Ingredient, Recipe, IngredientRecipes,
                     ShoppingCart, Favourite)


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSubscribSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientRecipesSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')
    class Meta:
        model = IngredientRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')



class RecipeSerializers(ModelSerializer):
    tags = SlugRelatedField(
        queryset=Tag.objects.all(),
        slug_field='slug'
    )
    image = Base64ImageField()
    ingredient = IngredientRecipesSerializer(source='recipe_ingredient', many=True)
    is_favorited = SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = SerializerMethodField('get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredient', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get['request']
        user = request.user
        return Favourite.objects.filter(user=user, recipe=obj)

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get['request']
        user = request.user
        return ShoppingCart.objects.filter(user=user, recipe=obj)