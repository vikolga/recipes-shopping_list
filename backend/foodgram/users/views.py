from django.shortcuts import get_object_or_404, render
from djoser.views import UserViewSet
from requests import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from api.permissions import AuthorOrReadOnly
from .models import CustomUser, Subscribed
from recipes.serializers import SubscribedSerializer
from .serializers import UserCreateSerializer, UserSerializer
from recipes.serializers import SubscribedSerializer

# Create your views here.
class UserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination #Заменить паджинатор на кастомный с limit
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['post', 'delete'])
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(CustomUser, id=self.kwargs.get('id'))
        
        if request.method == 'POST':
            if author == request.user:
                return Response(
                    {'errors': 'Вы пытаетесь подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscribed.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribedSerializer(author,
                                              context={'request': request})
            Subscribed.objects.create(user=user, author=author)
            return Response(serializer.data, {'message': 'Вы подписались на автора'}, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscript = get_object_or_404(Subscribed, user=user, author=author)
            subscript.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status)

    @action(detail=False,
            permission_classes=[IsAuthenticated],
            methods=('GET',))
    def subscriptions(self, request):
        user = self.request.user
        authors = CustomUser.objects.filter(subscribing__user=user)
        serializer = SubscribedSerializer(self.paginate_queryset(authors),
                                          many=True,
                                          context={'request':request})
        return self.get_paginated_response(serializer.data)

