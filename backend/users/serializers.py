import datetime as dt

from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework import serializers

from recipes.errors import ErrorResponse
from django.conf import settings
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели юзера."""
    role = serializers.ChoiceField(choices=settings.USERS_ROLE, default='user')
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True,
        validators=[
            UniqueValidator(
                queryset=CustomUser.objects.all(),
                message=ErrorResponse.USERNAME_EXISTS
            )]
    )
    email = serializers.CharField(
        max_length=254,
        required=True,
        validators=[
            UniqueValidator(
                queryset=CustomUser.objects.all(),
                message=ErrorResponse.EMAIL_EXISTS
            )]
    )

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
        )
        model = CustomUser


class ProfileSerializer(UserSerializer):
    role = serializers.CharField(read_only=True)


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=254,
        required=True
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        user_same_username = CustomUser.objects.filter(username=username).first()
        user_same_email = CustomUser.objects.filter(email=email).first()
        if user_same_username and user_same_username.email != email:
            raise serializers.ValidationError(ErrorResponse.USERNAME_EXISTS)
        if user_same_email and user_same_email.username != username:
            raise serializers.ValidationError(ErrorResponse.EMAIL_EXISTS)
        return data

    @staticmethod
    def validate_username(username):
        if username.lower() == settings.ME:
            raise serializers.ValidationError(ErrorResponse.FORBIDDEN_NAME)
        return username


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)

    def validate(self, data):
        username = data.get('username')
        if username is None:
            raise serializers.ValidationError(ErrorResponse.MISSING_USERNAME)
        return data
