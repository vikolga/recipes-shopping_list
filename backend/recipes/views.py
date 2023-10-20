from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from api.permissions import AuthorOrReadOnly, AdminOrReadOnly
from api.paginations import CustomPageNumberPaginator
from api.filters import IngredientFilter, RecipeFilter
from .models import Tag, Ingredient, Recipe, ShoppingCart, Favourite, IngredientRecipes
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeListSerializer, ShoppingCartSerializer,
                          RecipeSubscribSerializer, FavoriteSerializer,
                          IngredientRecipesSerializer, RecipeCreateUpdateSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeCreateUpdateSerializers
    # permission_classes = (IsAuthenticated,)
    pagination_class = CustomPageNumberPaginator
    filter_backends = [filters.SearchFilter, DjangoFilterBackend,]
    search_fields = ['^ingredients',]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list' or 'retrieve':
            return RecipeListSerializer
        elif self.action == 'create' or 'update':
            return RecipeCreateUpdateSerializer
    
    def get_permissions(self):
        if self.action == 'update' or 'destroy':
            return (AuthorOrReadOnly(), AdminOrReadOnly(), )
        if self.action == 'create':
            return (IsAuthenticated(), )
        


    @action(detail=True,
            permission_classes=[IsAuthenticated],
            url_path='shopping_cart', url_name='shopping_cart',
            methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        user = request.user
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
                get_object_or_404(ShoppingCart,
                                  user=user, recipe__id=pk).delete()
                return Response(
                    {'message': 'Рецепт удален из избранного'},
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Рецепт не был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(status)

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['post', 'delete'])
    def favorite(self, request, pk):
        user = request.user
        
        if request.method == 'POST':
            # serializer = FavoriteSerializer(
            #     data={'user': user.id, 'recipe': recipe.id},
            #     context={'request': request}
            # )
            # serializer.is_valid(raise_exception=True)
            # serializer.save()
            recipe = get_object_or_404(Recipe, id=pk)
            Favourite.objects.create(user=user, recipe=recipe)
            serializer = RecipeSubscribSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            if Favourite.objects.filter(user=user, recipe__id=pk).exists():
                get_object_or_404(Favourite, user=user, recipe__id=pk).delete()
                return Response(
                    {'message': 'Рецепт удален из избранного'},
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Рецепт не был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(status)

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            url_path='download_shopping_cart',
            url_name='download_shopping_cart',
            methods=['get'])
    def download_shopping_cart(self, request, **kwargs):
        user = request.user
        if user.is_anonymous:
            return Response(
                {'error': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED)
        list_shopping = 'Список покупок: '
        ingredients = IngredientRecipes.objects.filter(
            recipe__shopping_cart__user=user
        ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
            amounts=Sum('amount')
        )
        for i in enumerate(ingredients):
            list_shopping += (f'\n{i["ingredient__name"]} - '
                              f'{i["amounts"]} '
                              f'{i["ingredient__measurement_unit"]}'
                              )
        file = 'shopping_cart'
        response = HttpResponse(list_shopping, 'Content-Type: application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
        return response
