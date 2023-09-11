from django.contrib import admin
from .models import Subscribed, CustomUser

# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'password', 'first_name', 'last_name')


class SubscribedAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


admin.site.register(Subscribed, SubscribedAdmin)
admin.site.register(CustomUser, CustomUserAdmin)