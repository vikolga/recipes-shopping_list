from django.shortcuts import get_object_or_404, render
from djoser.views import UserViewSet
from requests import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from api.permissions import AuthorOrReadOnly
from .models import CustomUser, Subscribed
from .serializers import UserSerializer, SubscribedSerializer, UserCreateSerializer


# Create your views here.
class UserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    #serializer_class = UserSerializer
    #permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination #Заменить паджинатор на кастомный с limit
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['post', 'delete'])
    def subscribed(self, request, **kwargs):
        user = self.request.user
        author = get_object_or_404(CustomUser, id=self.kwargs.get('id'))
        if request.method == 'POST':
            serializer = SubscribedSerializer(author, context={'request':request})
            serializer.is_valid(raise_exception=True)
            Subscribed.objects.create(author=author, user=user)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            Subscribed.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=[IsAuthenticated],
            methods='GET')
    def subscription(self, request):
        user = self.request.user
        queryset = CustomUser.objects.filter(subscribing__user=user)
        serializer = SubscribedSerializer(self.paginate_queryset(queryset),
                                          many=True,
                                          context={'request':request})
        return self.get_paginated_response(serializer.data)

