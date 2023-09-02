from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""
    username = models.CharField(
        verbose_name='Name_user',
        help_text='Имя пользователя',
        max_length=150,
        unique=True,
    )
    password = models.CharField(
        verbose_name='password_user',
        max_length=100,
        blank=True,
        null=True,
    )
    email = models.EmailField(
        verbose_name='email_user',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='firstname_user',
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name='lastname_user',
        max_length=150,
        blank=True,
    )
    role = models.CharField(
        verbose_name='role_user',
        max_length=25,
        choices=settings.USERS_ROLE,
        default=settings.USER,
    )

    @property
    def is_admin(self):
        return (self.role == settings.ADMIN or self.is_superuser)

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='user_subscript',
        help_text='Подписчик на автора рецепта',
    )
    author = models.ForeignKey(
        CustomUser, null=True,
        on_delete=models.CASCADE,
        related_name='subscribes',
        verbose_name='author_subscript',
        help_text='Автор рецепта',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=['author', 'user'],
            name='unique_object'
        )]
    
    def __str__(self):
        return f'Подписка {self.user} на {self.author}'
