from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import TagViewSet, IngredientViewSet, RecipeViewSet
from users.views import UserViewSet


app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
