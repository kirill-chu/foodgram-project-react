from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser import views as djviews

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

    @action(detail=False, methods=['GET'])
    def me(self, request):
        if request.method == 'GET':
            user = request.user
            serializer = self.get_serializer(user, many=False)
            return Response(serializer.data)


class SignupViewset(CreateViewset):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
