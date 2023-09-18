from rest_framework.serializers import SerializerMethodField
from djoser.serializers import UserSerializer as UserDjoserSerializer
from djoser.serializers import UserCreateSerializer
from rest_framework import status
from rest_framework.fields import SerializerMethodField
from rest_framework.exceptions import ValidationError

from .models import Subscribed, CustomUser
from recipes.serializers import RecipeSubscribSerializer

class UserSerializer(UserDjoserSerializer):
    is_subscribed = SerializerMethodField(
        'get_is_subscribed',
        read_only=True
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscribed.objects.filter(user=user, author=obj).exists()
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 
                  'last_name', 'is_subscribed')
    # Посмотреть почему анониму не видно список всех пользователей


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class SubscribedSerializer(UserSerializer):
    recipes_count = SerializerMethodField('get_count_recipes')
    recipes = SerializerMethodField('get_recipes')

    class Meta():
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()
    
    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        limit = self.context.get['request'].query_params.get['limit']
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeSubscribSerializer(recipes, many=True, read_only=True).data
    

    def validate(self, data):
        # проверить как работает валидация с обработкой ошибок при подписке
        user = self.context.get['request'].user
        author = self.context.get['request'].author
        if Subscribed.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                'Вы подписаны на данного пользователя!',
                code=status.HTTP_400_BAD_REQUEST)
        if user == author:
            raise ValidationError(
                'Подписаться на самого себя нельзя',
                code=status.HTTP_400_BAD_REQUEST)

        return data
