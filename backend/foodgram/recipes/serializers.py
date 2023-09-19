from django.forms import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (ModelSerializer,
SerializerMethodField, ReadOnlyField, PrimaryKeyRelatedField)
from rest_framework import status
from users.serializers import UserSerializer
from users.models import CustomUser, Subscribed

from .models import (Tag, Ingredient, Recipe, IngredientRecipes,
                     ShoppingCart, Favourite)



class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        #read_only_fields = '__all__'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        #read_only_fields = '__all__'


class RecipeSubscribSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        #read_only_fields = '__all__'


class IngredientRecipesSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')
    class Meta:
        model = IngredientRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializers(ModelSerializer):
    tags = Tag.objects.all()
    author = PrimaryKeyRelatedField(read_only=True)
    image = Base64ImageField()
    ingredient = SerializerMethodField('get_ingredient')
    is_favorited = SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = SerializerMethodField('get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredient', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return Favourite.objects.filter(user=user, recipe=obj).exists()
    
    def get_ingredient(self, obj):
        ingredient = IngredientRecipes.objects.filter(recipe=obj)
        return IngredientRecipesSerializer(ingredient, many=True).data

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
    
class SubscribedSerializer(UserSerializer):
    recipes_count = SerializerMethodField('get_recipes_count')
    recipes = SerializerMethodField('get_recipes')

    class Meta():
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()
    
    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        limit = self.context.get('request').query_params.get('limit')
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeSubscribSerializer(recipes, many=True, read_only=True).data
    

    def validate(self, data):
        # проверить как работает валидация с обработкой ошибок при подписке
        user = self.context.get('request').user
        author = self.context.get('request').author
        if Subscribed.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                'Вы подписаны на данного пользователя!',
                code=status.HTTP_400_BAD_REQUEST)
        if user == author:
            raise ValidationError(
                'Подписаться на самого себя нельзя',
                code=status.HTTP_400_BAD_REQUEST)

        return data