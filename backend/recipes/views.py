from datetime import datetime
from rest_framework import status, filters
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.decorators import action

from api.permissions import AuthorOrReadOnly, AdminOrReadOnly
from api.paginations import CustomPageNumberPaginator
from api.filters import IngredientFilter, RecipeFilter
from .models import (Tag, Ingredient, Recipe, ShoppingCart,
                     Favourite, IngredientRecipes)
from .serializers import (RecipeCreateUpdateSerializer, IngredientSerializer,
                          RecipeListSerializer, ShoppingCartSerializer,
                          RecipeSubscribSerializer, TagSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    '''Вьюсет обработки запроса тегов.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    '''Вьюсет обработки запроса ингредиентов.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    '''Вьюсет обработки запроса рецептов.'''
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

    @action(detail=True,
            permission_classes=[IsAuthenticated],
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
                    {'message': 'Рецепт удален из избранного.'},
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Рецепт не был добавлен в избранное.'},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(status)

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['post', 'delete'])
    def favorite(self, request, pk):
        user = request.user
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            Favourite.objects.create(user=user, recipe=recipe)
            serializer = RecipeSubscribSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            if Favourite.objects.filter(user=user, recipe__id=pk).exists():
                get_object_or_404(Favourite, user=user, recipe__id=pk).delete()
                return Response(
                    {'message': 'Рецепт удален из избранного.'},
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Рецепт не был добавлен в избранное.'},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(status)

    @action(detail=False,
            permission_classes=[IsAuthenticated],)
    def download_shopping_cart(self, request):
        user = request.user
        if user.is_anonymous:
            return Response(
                {'error': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED)
        ingredients = IngredientRecipes.objects.filter(
            recipe__shopping_cart__user=user
        ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
            amount=Sum('amount')
        )
        data_shopping_cart = datetime.today()
        list_shopping = (f'Список покупок из рецептов от'
                         f'{data_shopping_cart:%d.%m.%Y}\n')
        list_shopping += '\n'.join([
            f'- {ingredient["ingredient__name"]}'
            f'({ingredient["ingredient__measurement_unit"]}) : '
            f'{ingredient["amount"]}'
            for ingredient in ingredients
        ])
        file = 'shopping_cart.txt'
        response = HttpResponse(list_shopping, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file}'
        return response
