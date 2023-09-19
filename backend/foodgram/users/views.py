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
    #permission_classes = (IsAuthenticatedOrReadOnly,)
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
            serializer = SubscribedSerializer(author, data=request.data, context={'request': self.request})
            serializer.is_valid()
            Subscribed.objects.create(user=user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscript = get_object_or_404(Subscribed, user=user, author=author)
            if not subscript:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if user.is_anonymous:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            subscript.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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

