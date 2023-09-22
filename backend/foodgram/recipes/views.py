from ipaddress import summarize_address_range
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet


from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from api.permissions import AuthorOrReadOnly, AdminOrReadOnly
from api.paginations import CustomPageNumberPaginator
from .models import Tag, Ingredient, Recipe, ShoppingCart, Favourite, IngredientRecipes
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
    pagination_class = CustomPageNumberPaginator

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
    
    @action(detail=True,
            permission_classes=[IsAuthenticated],
            url_path='download_shopping_cart', url_name='download_shopping_cart',
            methods=['get'])
    def download_shopping_cart(self, request):
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
            list_shopping +=(f'\n{i["ingredient__name"]} - '
                             f'{i["amounts"]} {i["ingredient__measurement_unit"]}'
                             )
        file = 'shopping_cart'
        response = HttpResponse(list_shopping, 'Content-Type: application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
        return response
