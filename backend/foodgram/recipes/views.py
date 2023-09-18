from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializers
from .models import Tag, Ingredient, Recipe
from rest_framework.permissions import IsAuthenticated
from api.permissions import AuthorOrReadOnly, AdminOrReadOnly
from rest_framework.pagination import PageNumberPagination

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
    permission_classes = (IsAuthenticated,)