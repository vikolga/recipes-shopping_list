from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, render
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet


from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action

from api.permissions import AuthorOrReadOnly, AdminOrReadOnly
from .models import Tag, Ingredient, Recipe, ShoppingCart, Favourite
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializers, ShoppingCartSerializer,
                          RecipeSubscribSerializer, FavoriteSerializer)

# Create your views here.
class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializers
    permission_classes = (AuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    
    @action(detail=True,
            permission_classes=[IsAuthenticated],
            url_path='shopping_cart', url_name='shopping_cart',
            methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        user=request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = ShoppingCartSerializer(
            data={'user': user.id, 'recipe': recipe.id}
        )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=request.user)
            serializer = RecipeSubscribSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if ShoppingCart.objects.filter(user=user, recipe__id=pk).exists():
                get_object_or_404(ShoppingCart, user=user, recipe__id=pk).delete()
                return Response(
                    {'message': 'Рецепт удален из избранного'},
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Рецепт не был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(status)

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            url_path='favorite', url_name='favorite',
            methods=['post', 'delete'])
    def favorite(self, request, pk):
        user=request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteSerializer(
            data={'user': user.id, 'recipe': recipe.id}
        )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=request.user)
            serializer = RecipeSubscribSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if Favourite.objects.filter(user=user, recipe__id=pk).exists():
                get_object_or_404(Favourite, user=user, recipe__id=pk).delete()
                return Response(
                    {'message': 'Рецепт удален из избранного'},
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Рецепт не был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(status)
