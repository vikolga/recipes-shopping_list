from rest_framework import status, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.decorators import action

from api.permissions import AuthorOrReadOnly, AdminOrReadOnly
from api.paginations import CustomPageNumberPaginator
from api.filters import IngredientFilter, RecipeFilter
from api.utils import get_shopping_cart
from .models import (Tag, Ingredient, Recipe, ShoppingCart,
                     Favourite)
from api.serializers import (RecipeCreateUpdateSerializer,
                             IngredientSerializer,
                             RecipeListSerializer,
                             TagSerializer, RecipeSubscribSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет обработки запроса тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет обработки запроса ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    """Вьюсет обработки запроса рецептов."""
    queryset = Recipe.objects.all()
    serializer = RecipeCreateUpdateSerializer
    pagination_class = CustomPageNumberPaginator
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ['^ingredients', ]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateUpdateSerializer

    def get_permissions(self):
        if self.action == 'update' or 'destroy':
            return (AuthorOrReadOnly(), )
        if self.action == 'create':
            return (IsAuthenticated(), )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_shop_favor_function(self, request, pk, models):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if not models.objects.filter(user=self.request.user,
                                         recipe=recipe).exists():
                models.objects.create(user=self.request.user,
                                      recipe=recipe)
                serializer = RecipeSubscribSerializer(recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response('errors: Объект уже в списке.',
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if models.objects.filter(user=self.request.user,
                                     recipe=recipe).exists():
                models.objects.filter(user=self.request.user,
                                      recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response('errors: Объект не в списке.',
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        return self.get_shop_favor_function(
            request, pk, ShoppingCart)

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['post', 'delete'])
    def favorite(self, request, pk):
        return self.get_shop_favor_function(
            request, pk, Favourite)

    @action(detail=False,
            permission_classes=[IsAuthenticated],)
    def download_shopping_cart(self, request):
        return get_shopping_cart(request.user)
