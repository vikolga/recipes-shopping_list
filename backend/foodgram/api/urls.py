from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet
from recipes.views import TagViewSet, IngredientViewSet, RecipeViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)



urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]