from django.forms import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from drf_extra_fields.fields import Base64ImageField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import (ModelSerializer,
                                        SerializerMethodField, ReadOnlyField,
                                        PrimaryKeyRelatedField, IntegerField)

from users.serializers import UserSerializer
from users.models import CustomUser, Subscribed
from .models import (Tag, Ingredient, Recipe, IngredientRecipes,
                     ShoppingCart, Favourite)


class TagSerializer(ModelSerializer):
    '''Сериализатор тегов.'''
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    '''Сериализатор ингредиентов.'''
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSubscribSerializer(ModelSerializer):
    '''Сериализатор рецепта короткого вида.'''
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientRecipesSerializer(ModelSerializer):
    '''Сериализатор промежуточной модели ингредиентов в рецептах.'''
    id = PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientRecipeCreateSerializer(ModelSerializer):
    '''Сериализатор промежуточной модели ингредиентов в рецептах
    для создания рецепта.'''
    id = IntegerField()

    class Meta:
        model = IngredientRecipes
        fields = ('id', 'amount')


class RecipeListSerializer(ModelSerializer):
    '''Сериализатор вывода списка рецептов.'''
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientRecipesSerializer(many=True,
                                              source='ingredient_used')
    is_favorited = SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = SerializerMethodField('get_is_in_shopping_cart',
                                                read_only=True)

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


class RecipeCreateUpdateSerializer(ModelSerializer):
    '''Сериализатор создания и редактуры рецепта.'''
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    ingredients = IngredientRecipeCreateSerializer(many=True,
                                                   source='ingredient_used')
    cooking_time = IntegerField()
    author = UserSerializer(read_only=True)
    author = SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'author',
                  'name', 'image', 'text', 'cooking_time')

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError(
                {'Добавьте хотя бы один ингридиент.'}
                )
        ingredients_list = []
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(Ingredient,
                                                   id=ingredient['id'])
            if ingredient in ingredients_list:
                raise ValidationError({'Ингридиенты должны быть уникальными.'})
            if int(ingredient['amount']) < 1:
                raise ValidationError(
                    {'Должна быть хотя бы 1 единица ингредиента.'}
                    )
            ingredients_list.append(current_ingredient)
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError({'Добавьте хотя бы один тег.'})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({'Теги должны быть уникальными!'})
            tags_list.append(tag)
        return value

    def validate_cooking_time(self, value):
        cooking_time = value
        if cooking_time < 1:
            raise ValidationError({'Минимальное время готовки - 1 минута.'})
        return value

    def create_ingredients(self, ingredients, recipe):
        context = self.context['request']
        current_ingredients = context.data['ingredients']
        for ingredient in current_ingredients:
            current_ingredient = Ingredient.objects.get(id=ingredient['id'])
            IngredientRecipes.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient['amount'],
            )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient_used')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredient_used')
        recipe = instance
        IngredientRecipes.objects.filter(recipe=recipe).delete()
        self.create_ingredients(ingredients, recipe)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeListSerializer(instance,
                                    context={'request': request}).data


class ShoppingCartSerializer(ModelSerializer):
    '''Сериализатор списка покупок.'''
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
                {'Рецепт уже был добавлен в список покупок.'}
                )
        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        return validated_data


class SubscribedSerializer(UserSerializer):
    '''Сериализатор подписок.'''
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
            raise ValidationError('Вы подписаны на данного пользователя.')
        if user == author:
            raise ValidationError('Подписаться на самого себя нельзя.')
        return data


class FavoriteSerializer(ModelSerializer):
    '''Сериализатор издранного.'''
    user = IntegerField(source='user.id')
    recipe = IntegerField(source='recipe.id')

    class Meta():
        model = Favourite
        fields = '__all__'

    def validate(self, data):
        user = data['user']['id']
        recipe = data['recipe']['id']
        if Favourite.objects.filter(user=user, recipe__id=recipe).exists():
            raise ValidationError({'Рецепт уже в избранном.'})
        return data

    def create(self, validated_data):
        user = validated_data.get('user')
        recipe = validated_data.get('recipe')
        Favourite.objects.get_or_create(user=user, recipe=recipe)
        return validated_data
