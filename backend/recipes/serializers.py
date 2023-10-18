from django.forms import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (ModelSerializer,
                                        SerializerMethodField, ReadOnlyField,
                                        PrimaryKeyRelatedField, IntegerField)
from rest_framework import status
from users.serializers import UserSerializer
from users.models import CustomUser, Subscribed

from .models import (Tag, Ingredient, Recipe, IngredientRecipes,
                     ShoppingCart, Favourite, TagRecipes)


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        # read_only_fields = '__all__'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        # read_only_fields = '__all__'


class RecipeSubscribSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        # read_only_fields = '__all__'


class IngredientRecipesSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientRecipeCreateSerializer(ModelSerializer):
    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = IngredientRecipes
        fields = ('id', 'amount')


class RecipeListSerializers(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientRecipesSerializer(many=True,
                                              source='ingredient_used')
    is_favorited = SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = SerializerMethodField('get_is_in_shopping_cart',
                                                read_only=True)
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

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


class RecipeCreateUpdateSerializers(ModelSerializer):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    ingredients = IngredientRecipeCreateSerializer(many=True,
                                                   source='ingredient_used')
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate(self, obj):
        for field in ['name', 'text', 'cooking_time']:
            if not obj.get(field):
                raise ValidationError(
                    f'{field} - Обязательное поле.'
                )
        if not obj.get('tags'):
            raise ValidationError(
                'Нужно указать минимум 1 тег.'
            )
        ingredients_list = []
        for ingredient in obj.get('recipe_used'):
            if ingredient.get('amount') <= 0:
                raise ValidationError(
                    'Количество не может быть меньше 1'
                )
            ingredients_list.append(ingredient.get('id'))
        inrgedient_id_list = [item['id'] for item in obj.get('ingredients')]
        unique_ingredient_id_list = set(inrgedient_id_list)
        if len(inrgedient_id_list) != len(unique_ingredient_id_list):
            raise ValidationError(
                'Ингредиенты должны быть уникальны.'
            )
        return obj

    @transaction.atomic
    # def create(self, validated_data):
    #     request = self.context.get('request')
    #     ingredients = validated_data.pop('ingredients')
    #     tags = validated_data.pop('tags')
    #     recipe = Recipe.objects.create(author=request.user, **validated_data)
    #     recipe.tags.set(tags)
    #     for i in ingredients:
    #         ingredient = Ingredient.objects.get(id=i['id'])
    #         IngredientRecipes.objects.create(
    #             ingredient=ingredient, recipe=recipe, amount=i['amount']
    #         )
    #     recipe.save()
    #     return recipe
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('recipe_used')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        ingredient_list = []
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(Ingredient,
                                                   id=ingredient.get('id'))
            amount = ingredient.get('amount')
            ingredient_list.append(
                IngredientRecipes(
                    recipe=recipe,
                    ingredient=current_ingredient,
                    amount=amount
                )
            )
        IngredientRecipes.objects.bulk_create(ingredient_list)
        return recipe

    # def update(self, instance, validated_data):
    #     pass

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeListSerializers(instance,
                                     context={'request': request}).data


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
        request = self.context.get('request')
        recipes = obj.recipes.all()
        limit = request.GET.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeSubscribSerializer(recipes,
                                        many=True, read_only=True).data

    def validate(self, data):
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
        user = validated_data.get('user')
        recipe = validated_data.get('recipe')
        Favourite.objects.get_or_create(user=user, recipe=recipe)
        return validated_data
