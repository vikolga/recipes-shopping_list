from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer

from .models import Subscribed, CustomUser

class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscribed.objects.filter(user=user, author=obj).exists()
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 
                  'last_name', 'is_subscribed')
        


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
