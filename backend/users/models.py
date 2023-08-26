from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True
    )
    password = models.CharField(
        max_length=100,
        blank=True,
        null=True)
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(
        'Статус пользователя',
        max_length=25,
        choices=settings.USERS_ROLE,
        default=settings.USER
    )

    @property
    def is_admin(self):
        return (self.role == settings.ADMIN or self.is_superuser)

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username

