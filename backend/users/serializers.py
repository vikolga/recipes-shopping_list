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
        if user.is_anonymous:
            return False
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
