from requests import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, render
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from .models import Tag, Ingredient, Recipe, ShoppingCart, Favourite
from rest_framework.permissions import IsAuthenticated
from api.permissions import AuthorOrReadOnly, AdminOrReadOnly
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
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
            methods=['post', 'delete'])
    def shopping_cart(self, request, **kwargs):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('id'))
        if request.method == 'POST':
            
            serializer = ShoppingCartSerializer(
                data={'user': user, 'recipe': recipe},
                context={'request': request}
            )
            serializer.is_valid()
            serializer.save(recipe=recipe, user=user)
            serializer = RecipeSubscribSerializer
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            ShoppingCart.objects.get_or_create(user=user, recipe=recipe).delete()
            return Response(
                {'message': 'Рецепт удален из списка покупок'},
                status=status.HTTP_204_NO_CONTENT)
        #return Response(
             #   {'error': 'Неверный тип запроса'},
             #   status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['post', 'delete'])
    def favorite(self, request, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('id'))
        if request.method == 'POST':
           serializer = RecipeSubscribSerializer(recipe,
                                                 context={'request': request})
           Favourite.objects.create(user=user, recipe=recipe)
           return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if Favourite.objects.filter(user=user, recipe=recipe).exists():
                get_object_or_404(Favourite, user=user, recipe=recipe).delete()
                return Response(
                    {'message': 'Рецепт удален из избранного'},
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Рецепт не был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(status)
