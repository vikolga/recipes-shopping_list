from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from users.views import CustomUserViewSet
from rest_framework.routers import DefaultRouter

from recipes.views import IngredientViewSet, RecipesViewSet, TagViewSet


router_v1 = DefaultRouter()
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('recipes', RecipesViewSet)
router_v1.register('tags', TagViewSet)
router_v1.register('users', CustomUserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('router_v1.urls')),
    path('api/auth/', include('djoser.urls.authtoken'))
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )