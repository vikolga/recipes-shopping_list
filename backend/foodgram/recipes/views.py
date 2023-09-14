from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from .serializers import TagSerializer
from .models import Tag
from api.permissions import AuthorOrReadOnly, AdminOrReadOnly
from rest_framework.pagination import PageNumberPagination

# Create your views here.
class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)