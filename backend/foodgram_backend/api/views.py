from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Ingredient, Tag, Recipe, Follow
from .serializers import (
    CustomUserSerializer, FollowSerializer, IngredientSerializer,
    RecipeSerializer, RecipeWriteSerializer, TagSerializer,
    TempFollowSerializer
)

User = get_user_model()


class CreateViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Базовый вьюсет только для создания."""


class UserViewset(viewsets.ModelViewSet):
    """Вьюсет для создания пользователя."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None

    @action(detail=False, methods=['GET'])
    def me(self, request):
        if request.method == 'GET':
            user = request.user
            serializer = self.get_serializer(user, many=False)
            return Response(serializer.data)

    @action(detail=False, methods=['DELETE', 'POST'],
            url_path=r'(?P<id>\d+)/subscribe',
            serializer_class=FollowSerializer)
    def subscribe(self, request, id):
        if request.method == 'DELETE':
            following = User.objects.get(id=id)
            follow = get_object_or_404(Follow, user=request.user,
                                       following_id=id)
            follow.delete()
            return Response(status=status.HTTP_200_OK)

        elif request.method == 'POST':
            following = User.objects.get(id=id)
            if Follow.objects.filter(user=request.user,
                                     following=following).exists():
                response = {
                    'detail': 'You have already subscribed.'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=request.user,
                                  following=following)
            serializer = CustomUserSerializer(following, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        subs = User.objects.filter(following__user=request.user)
        serializer = TempFollowSerializer(subs, many=True,
                                          context={'request': request})
        return Response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингридиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if (self.action == 'list') or (self.action == 'retrieve'):
            return RecipeSerializer
        return RecipeWriteSerializer


class CommonListCreateDestroyViewSet(mixins.DestroyModelMixin,
                                     mixins.RetrieveModelMixin,
                                     mixins.CreateModelMixin,
                                     viewsets.GenericViewSet):
    """Общий базовый вьюсет list/create."""
