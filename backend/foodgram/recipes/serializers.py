from django.forms import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (ModelSerializer,
SerializerMethodField, ReadOnlyField, PrimaryKeyRelatedField, IntegerField)
from rest_framework import status
from users.serializers import UserSerializer
from users.models import CustomUser, Subscribed

from .models import (Tag, Ingredient, Recipe, IngredientRecipes,
                     ShoppingCart, Favourite, TagRecipe)



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
    id = PrimaryKeyRelatedField(
        queryset = Ingredient.objects.all(),
        source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')
    class Meta:
        model = IngredientRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializers(ModelSerializer):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=True,)
    author = CustomUser(read_only=True)
    image = Base64ImageField()
    ingredient = IngredientRecipesSerializer(many=True, source='ingredient_used')
    is_favorited = SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = SerializerMethodField('get_is_in_shopping_cart', read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredient', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favourite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
    
    def create(self, validated_data):
        author = UserSerializer(read_only=True)
        context = self.context['request']
        ingredient = validated_data.pop('ingredient_used')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        current_ingredients = context.data['ingredient']
        for ingredient in current_ingredients:
            current_ingredient = Ingredient.objects.get(id=ingredient['id'])
            IngredientRecipes.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient['amount'],
            )
        return recipe
    
    def update(self, instance, validated_data):
        context = self.context['request']
        ingredient = validated_data.pop('ingredient_used')
        recipe = instance
        IngredientRecipes.objects.filter(recipe=recipe).delete()
        current_ingredients = context.data['ingredient']
        for ingredient in current_ingredients:
            current_ingredient = Ingredient.objects.get(id=ingredient['id'])
            IngredientRecipes.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient['amount'],
            )
        return super().update(instance, validated_data)
    

class ShoppingCartSerializer(ModelSerializer):
    user = IntegerField(source='user.id')
    recipe = IntegerField(source='recipe.id')

    class Meta():
        model = Favourite
        fields = '__all__'    

    def validate(self, data):
        user = data['user']['id']
        recipe = data['recipe']['id']
        if ShoppingCart.objects.filter(user=user, recipe__id=recipe).exists():
            raise ValidationError(
                {'errors': 'Рецепт уже был добавлен в список покупок'}
            )
        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        return validated_data
    
    
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


class FavoriteSerializer(ModelSerializer):
    user = IntegerField(source='user.id')
    recipe = IntegerField(source='recipe.id')

    class Meta():
        model = Favourite
        fields = '__all__'    

    def validate(self, data):
        user = data['user']['id']
        recipe = data['recipe']['id']
        if Favourite.objects.filter(user=user, recipe__id=recipe).exists():
            raise ValidationError(
                {'errors': 'Рецепт уже в избранном'}
            )
        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        Favourite.objects.get_or_create(user=user, recipe=recipe)
        return validated_data
