from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet
from recipes.views import TagViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('tags', TagViewSet)



urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]