from requests import Response
from rest_framework import status
from rest_framework.serializers import SerializerMethodField
from djoser.serializers import UserSerializer as UserDjoserSerializer
from djoser.serializers import UserCreateSerializer

from .models import Subscriber, CustomUser


class UserSerializer(UserDjoserSerializer):
    '''Сериализатор для вывода модели кастомного пользователя.'''
    is_subscribed = SerializerMethodField(
        'get_is_subscribed',
        read_only=True
    )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        author = self.context['request'].author
        if user.is_anonymous:
            return False
        if author == user:
            return Response(
                {'errors': 'Вы пытаетесь подписаться на себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscriber.objects.filter(user=user, author=author).exists():
            return Response(
                {'errors': 'Вы уже подписаны на данного автора.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Subscriber.objects.filter(user=user, author=obj).exists()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed')


class UserCreateSerializer(UserCreateSerializer):
    '''Сериализатор для создания пользователя.'''
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
