from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import CustomUser, Subscriber
from .serializers import UserCreateSerializer, UserSerializer
from recipes.serializers import SubscribedSerializer
from api.paginations import CustomPageNumberPaginator


class UserViewSet(UserViewSet):
    '''Вьюсет обработки запроса пользователей.'''
    queryset = CustomUser.objects.all()
    pagination_class = CustomPageNumberPaginator

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
                    {'errors': 'Вы пытаетесь подписаться на себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscriber.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribedSerializer(author,
                                              context={'request': request})
            Subscriber.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if Subscriber.objects.filter(user=user, author=author).exists():
                get_object_or_404(Subscriber, user=user,
                                  author=author).delete()
                return Response(
                    {'message': 'Вы отписались от автора.'},
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Вы не подписаны на данного автора.'},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(status)

    @action(detail=False,
            permission_classes=[IsAuthenticated],
            methods=('GET',))
    def subscriptions(self, request):
        user = request.user
        authors = CustomUser.objects.filter(subscribing__user=user)
        serializer = SubscribedSerializer(self.paginate_queryset(authors),
                                          many=True,
                                          context={'request': request})
        return self.get_paginated_response(serializer.data)
