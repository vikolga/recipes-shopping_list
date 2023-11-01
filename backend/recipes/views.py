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
from .serializers import (FavoriteSerializer, RecipeCreateUpdateSerializer,
                          IngredientSerializer,
                          RecipeListSerializer, ShoppingCartSerializer,
                          TagSerializer)


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

    def get_shop_favor_function(self, request, pk, model, model_serializer):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        data = {}
        data['recipe'] = recipe.pk
        data['favouriting'] = user.pk
        if request.method == 'POST':
            serializer = model_serializer(data=data,
                                          context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = RecipeListSerializer(recipe,
                                              context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        obj = get_object_or_404(model, favouriting=user,
                                recipe=recipe)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        # if request.method == 'POST':
        #     serializer = model_serializer(
        #         data={
        #             'user': request.user.id,
        #             'recipe': get_object_or_404(Recipe, id=id).id
        #         },
        #         context={'request': request}
        #     )
        #     serializer.is_valid(raise_exception=True)
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # del_model = get_object_or_404(model,
        #                               user=request.user,
        #                               recipe=get_object_or_404(Recipe,
        # id=id))
        # self.perform_destroy(del_model)
        # return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        return self.get_shop_favor_function(
            request, pk, ShoppingCart, ShoppingCartSerializer)
        # user = request.user
        # recipe = get_object_or_404(Recipe, id=pk)
        # serializer = ShoppingCartSerializer(
        #     data={'user': user.id, 'recipe': recipe.id}
        # )
        # if request.method == 'POST':
        #     serializer.is_valid(raise_exception=True)
        #     serializer.save(recipe=recipe, user=request.user)
        #     serializer = RecipeSubscribSerializer(recipe)
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # if request.method == 'DELETE':
        #     if ShoppingCart.objects.filter(user=user,
        # recipe__id=pk).exists():
        #         get_object_or_404(ShoppingCart,
        #                           user=user, recipe__id=pk).delete()
        #         return Response(
        #             {'message': 'Рецепт удален из избранного.'},
        #             status=status.HTTP_204_NO_CONTENT)
        #     return Response(
        #         {'error': 'Рецепт не был добавлен в избранное.'},
        #         status=status.HTTP_400_BAD_REQUEST)
        # return Response(status)

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['post', 'delete'])
    def favorite(self, request, pk):
        return self.get_shop_favor_function(
            request, pk, Favourite, FavoriteSerializer)
        # user = request.user
        # if request.method == 'POST':
        #     recipe = get_object_or_404(Recipe, id=pk)
        #     Favourite.objects.create(user=user, recipe=recipe)
        #     serializer = RecipeSubscribSerializer(recipe)
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # if request.method == 'DELETE':
        #     recipe = get_object_or_404(Recipe, id=pk)
        #     if Favourite.objects.filter(user=user, recipe__id=pk).exists():
        #         get_object_or_404(Favourite, user=user,
        # recipe__id=pk).delete()
        #         return Response(
        #             {'message': 'Рецепт удален из избранного.'},
        #             status=status.HTTP_204_NO_CONTENT)
        #     return Response(
        #         {'error': 'Рецепт не был добавлен в избранное.'},
        #         status=status.HTTP_400_BAD_REQUEST)
        # return Response(status)

    @action(detail=False,
            permission_classes=[IsAuthenticated],)
    def download_shopping_cart(self, request):
        user = request.user
        return get_shopping_cart(user)
