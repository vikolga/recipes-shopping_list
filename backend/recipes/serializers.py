from django.forms import ValidationError
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import (ModelSerializer,
                                        SerializerMethodField, ReadOnlyField,
                                        PrimaryKeyRelatedField, IntegerField)

from users.serializers import UserSerializer
from users.models import CustomUser, Subscriber
from .models import (Tag, Ingredient, Recipe, IngredientRecipes,
                     ShoppingCart, Favourite)


class TagSerializer(ModelSerializer):
    """Сериализатор тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    """Сериализатор ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSubscribSerializer(ModelSerializer):
    """Сериализатор рецепта короткого вида."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientRecipesSerializer(ModelSerializer):
    """Сериализатор промежуточной модели ингредиентов в рецептах."""
    id = PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientRecipeCreateSerializer(ModelSerializer):
    """Сериализатор промежуточной модели ингредиентов в рецептах
    для создания рецепта."""
    id = IntegerField()

    class Meta:
        model = IngredientRecipes
        fields = ('id', 'amount')


class RecipeListSerializer(ModelSerializer):
    """Сериализатор вывода списка рецептов."""
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
    """Сериализатор создания и редактуры рецепта."""
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

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise ValidationError({
                    'ingredient':
                    'Нельзя использовать два раза один ингредиент.'
                })
            ingredients_list.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) <= 0:
                raise ValidationError({
                    'amount': 'Минимальное количество ингредиентов 1.'
                })

        tags = self.initial_data.get('tags')
        if not tags:
            raise ValidationError({
                'tags': 'Нужно выбрать хотя бы один тег.'
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({
                    'tags': 'Теги не должны повторяться.'
                })
            tags_list.append(tag)

        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise ValidationError({
                'cooking_time':
                'Время приготовления не может быть менее 1 минуты.'
            })
        return data

    def create_ingredients(self, ingredients, recipe):
        IngredientRecipes.objects.bulk_create(
            [IngredientRecipes(recipe=recipe,
                               amount=ingredient['amount'],
                               ingredient=Ingredient.objects.get(
                                   id=ingredient['id']))
             for ingredient in ingredients]
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
        # recipe = instance
        IngredientRecipes.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeListSerializer(instance,
                                    context={'request': request}).data


class ShoppingCartSerializer(ModelSerializer):
    """Сериализатор списка покупок."""
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
                {'detail': 'Рецепт уже был добавлен в список покупок.'}
            )
        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        return validated_data


class SubscribedSerializer(UserSerializer):
    """Сериализатор подписок."""
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
        if Subscriber.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                {'detail': 'Вы подписаны на данного пользователя.'})
        if user == author:
            raise ValidationError(
                {'detail': 'Подписаться на самого себя нельзя.'})
        return data


class FavoriteSerializer(ModelSerializer):
    """Сериализатор издранного."""
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
