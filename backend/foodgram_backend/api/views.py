from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, permissions

from .serializers import (
    CustomUserCreateSerializer, SignupSerializer, UserSerializer
)

User = get_user_model()


class CreateViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Базовый вьюсет только для создания."""


class CreateUserViewset(viewsets.ModelViewSet):
    """Вьюсет для создания пользователя."""
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer
    permission_classes = (permissions.AllowAny,)


class SignupViewset(CreateViewset):
    queryset = User.objects.all()
    serializer_class = SignupSerializer


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
