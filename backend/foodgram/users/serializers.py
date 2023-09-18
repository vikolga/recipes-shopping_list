from rest_framework.serializers import SerializerMethodField
from djoser.serializers import UserSerializer as UserDjoserSerializer
from djoser.serializers import UserCreateSerializer
from rest_framework import status
from rest_framework.fields import SerializerMethodField

from .models import Subscribed, CustomUser

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

