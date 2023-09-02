from djoser.views import UserViewSet
from rest_framework import status, exceptions
from rest_framework.decorators import action
from rest_framework import filters, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer

from recipes.models import Tag, Ingredient, Recipe
from users.models import CustomUser, Subscription
from .serializers import (CustomUserSerializer, UserSubscribeSerializer)


#class TagViewSet(viewsets.ReadOnlyModelViewSet):
  #  queryset = Tag.objects.all()
  #  serializer_class = TagSerializers


#class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
 #  queryset = Ingredient.objects.all()
  #  serializer_class = IngredientSerializers
  #  filter_backends = (filters.SearchFilter)
  #  search_field = ('^name',)


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        methods=('get',),
        serializer_class=UserSubscribeSerializer,
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        user = self.request.user
        user_subscriptions = user.subscribes.all()
        authors = [item.author.id for item in user_subscriptions]
        queryset = CustomUser.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        serializer_class=UserSubscribeSerializer
    )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(CustomUser, pk=id)

        if self.request.method == 'POST':
            if user == author:
                raise exceptions.ValidationError(
                    'Подписка на самого себя запрещена.'
                )
            if Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError('Подписка уже оформлена.')

            Subscription.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError(
                    'Подписка не была оформлена, либо уже удалена.'
                )

            subscription = get_object_or_404(
                Subscription,
                user=user,
                author=author
            )
            subscription.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)