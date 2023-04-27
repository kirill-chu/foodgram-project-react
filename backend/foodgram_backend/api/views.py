from django.contrib.auth import get_user_model
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    CustomUserSerializer,
)

User = get_user_model()


class CreateViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Базовый вьюсет только для создания."""


class UserViewset(viewsets.ModelViewSet):
    """Вьюсет для создания пользователя."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny,)

    @action(detail=False, methods=['GET'])
    def me(self, request):
        if request.method == 'GET':
            user = request.user
            serializer = self.get_serializer(user, many=False)
            return Response(serializer.data)
