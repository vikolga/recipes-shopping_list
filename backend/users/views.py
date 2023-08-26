from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings

from users.serializers import (UserSerializer,
                             GetTokenSerializer,
                             SignUpSerializer,
                             ProfileSerializer)
from .models import CustomUser
from recipes.permissions import (IsAdmin,
                             IsAmdinOrReadOnly,
                             IsAdminModeratorOwnerOrReadOnly)
from recipes.paginations import (OtherPagination)
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import filters


class CustomUserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin, )
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = OtherPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)

    @action(
        methods=('get', 'patch'),
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,),
        serializer_class=ProfileSerializer
    )
    def set_profile(self, request, id=None):
        """Изменяет данные в профайле пользователя."""
        user = get_object_or_404(CustomUser, id=request.user.id)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def sign_up(request):
    """Регистрирует пользователя и отправляет код подтверждения."""
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user, _ = CustomUser.objects.get_or_create(**serializer.validated_data)
    user.confirmation_code = default_token_generator.make_token(user=user)
    send_mail(
        subject=settings.DEFAULT_EMAIL_SUBJECT,
        message=user.confirmation_code,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=(user.email,)
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_token(request):
    """"Выдает токен для авторизации."""
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(CustomUser, username=username)
    if confirmation_code != user.confirmation_code:
        return Response(request.data, status=status.HTTP_400_BAD_REQUEST)
    return Response({'token': str(AccessToken.for_user(user))},
                    status=status.HTTP_200_OK)