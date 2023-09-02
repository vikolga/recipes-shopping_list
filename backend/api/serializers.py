import traceback
from django.db import IntegrityError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Tag, Ingredient, Recipe,
                            IngredientsRecipe,
                            TagsRecipe, ShoppingCart, FavoriteRecipe)
from users.models import CustomUser, Subscription


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user

        if user.is_anonymous:
            return False

        return Subscription.objects.filter(user=user, author=obj).exists()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed')


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'password')


class UserSubscribeSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField('get_recipes')
    recipes_count = serializers.SerializerMethodField('get_recipes_count')
    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=CustomUser.objects.all()
        )]
    )

    def validate(self, data):
        author = data['subscribers']
        user = data['subscribes']
        if user == author:
            raise serializers.ValidationError('You can`t follow for yourself!')
        if (Subscription.objects.filter(author=author, user=user).exists()):
            raise serializers.ValidationError('You have already subscribed!')
        return data

    def create(self, validated_data):
        subscribe = Subscription.objects.create(**validated_data)
        subscribe.save()
        return subscribe

    def get_recipes_count(self, data):
        return Recipe.objects.filter(author=data).count()

    def get_recipes(self, data):
        recipes_limit = self.context.get('request').GET.get('recipes_limit')
        recipes = (
            data.recipes.all()[:int(recipes_limit)]
            if recipes_limit else data.recipes
        )
        serializer = serializers.ListSerializer(child=RecipeSerializer())
        return serializer.to_representation(recipes)
    
    class Meta:
        model = CustomUser
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'recipes', 'recipes_count', 'is_subscribed'
        ]
