from django.contrib import admin

from .models import Subscribed, CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    """ Модель администратора для пользователя """
    list_display = ('id', 'username', 'email', 'password',
                    'first_name', 'last_name')
    list_filter = ('username', 'email')


class SubscribedAdmin(admin.ModelAdmin):
    """ Модель администратора для подписок"""
    list_display = ('user', 'author')


admin.site.register(Subscribed, SubscribedAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
