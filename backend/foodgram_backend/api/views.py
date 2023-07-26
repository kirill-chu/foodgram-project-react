from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import Ingredient, Tag, Recipe, Follow, Favorite
from .filters import RecipeFilter
from .pagination import CustomPagination
from .serializers import (
    CustomUserSerializer, FavoriteSerializer, FollowSerializer,
    IngredientSerializer, RecipeSerializer, RecipeWriteSerializer,
    TagSerializer, TempFollowSerializer
)

User = get_user_model()


class CreateViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Базовый вьюсет только для создания."""


class UserViewset(viewsets.ModelViewSet):
    """Вьюсет для создания пользователя."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = CustomPagination

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
            return Response(status=status.HTTP_204_NO_CONTENT)

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
            serializer = CustomUserSerializer(
                following, many=False, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        if not request.user.is_authenticated:
            response = {'detail': 'Учетные данные не были предоставлены.'}
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

        subs = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(subs)
        serializer = TempFollowSerializer(page, many=True,
                                          context={'request': request})

        return self.get_paginated_response(serializer.data)


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

    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = Recipe.objects.all()
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):

        if (self.action == 'list') or (self.action == 'retrieve'):
            return RecipeSerializer
        return RecipeWriteSerializer

    @action(detail=False, methods=['DELETE', 'POST'],
            url_path=r'(?P<id>\d+)/favorite',
            serializer_class=FollowSerializer)
    def favorite(self, request, id):
        if request.method == 'DELETE':
            favorite = get_object_or_404(Favorite, user=request.user,
                                         recipe_id=id)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.method == 'POST':
            if Favorite.objects.filter(user=request.user,
                                       recipe_id=id).exists():
                response = {
                    'detail': 'This recipe is already in favorites.'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            favorite = Favorite.objects.create(
                user=request.user, recipe_id=id)
            serializer = FavoriteSerializer(
                favorite, many=False, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CommonListCreateDestroyViewSet(mixins.DestroyModelMixin,
                                     mixins.RetrieveModelMixin,
                                     mixins.CreateModelMixin,
                                     viewsets.GenericViewSet):
    """Общий базовый вьюсет list/create."""
