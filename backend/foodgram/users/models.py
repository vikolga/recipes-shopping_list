from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    """Кастомная модель пользователя от AbstractUser"""
    
    username = models.CharField(
        max_length=150,
        unique=True
    )
    first_name = models.CharField(
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        blank=True
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    password = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['username',]

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'


class Subscribed(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='subscriber',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='subscribing',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscrib'
            ),
        ]
    
    def __str__(self) -> str:
        return f'Подписчик {self.user}, автор {self.author}'