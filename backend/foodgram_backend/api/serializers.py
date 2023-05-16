import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


from recipes.models import (
    Follow, Ingredient, IngredientRecipe, Tag, TagRecipe, Recipe)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='recipe.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
            'is_subscribed'
        )

    def create(self, validated_data):
        user = User(email=validated_data['email'],
                    username=validated_data['username'],
                    first_name=validated_data['first_name'],
                    last_name=validated_data['last_name']
                    )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        user = (self.context.get('request').user)
        return obj.following.filter(user=user).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для Тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для Ингридиентов."""

    measurement_unit = serializers.SlugRelatedField(
        read_only=True, slug_field='unit_name')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для Ингридиентов."""

    measurement_unit = serializers.SlugRelatedField(
        read_only=True, slug_field='unit_name')
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'amount', 'measurement_unit')

    def get_amount(self, obj):
        values = obj.ingredientrecipe_set.values()
        if values:
            amount = values[0].get('amount')
            return amount


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для Ингридиентов."""

    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')

    def get_amount(self, obj):
        values = obj.ingredientrecipe_set.values()
        if values:
            amount = values[0].get('amount')
            return amount


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалейзер для рецептов."""

    author = CustomUserSerializer(read_only=True, many=False)
    ingredients = IngredientRecipeSerializer(read_only=True, many=True)
    tags = TagSerializer(many=True, read_only=True)

    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorite',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorite(self, obj):
        return False

    def get_is_in_shopping_cart(self, obj):
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи рецептов."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault())

    ingredients = IngredientRecipeWriteSerializer(read_only=True, many=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name', 'image', 'text',
                  'cooking_time', 'author')

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError('Нет игридиентов, нет рецепта!')
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError('Тег не выбран!')

        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')

        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(
                id=ingredient['id']
            )
            IngredientRecipe.objects.create(
                ingredient=current_ingredient,
                amount=ingredient['amount'], recipe=recipe
            )
        for tag in tags:
            current_tag = Tag.objects.get(id=tag)
            TagRecipe.objects.create(tag=current_tag, recipe=recipe)

        return recipe


class CurrentFollowingDefault:
    """Класс возвращает пользователя на которого подписывается другой."""

    requires_context = True

    def __call__(self, serializer_field):
        context = serializer_field.context['request'].parser_context
        return get_object_or_404(User, id=context.get('kwargs').get('id'))


class FollowSerializer(serializers.ModelSerializer):
    """Сериалайзер для подписок."""
    following = serializers.SlugRelatedField(
        slug_field='username', default=CurrentFollowingDefault(),
        read_only=True)
    user = serializers.SlugRelatedField(
        slug_field='username', default=serializers.CurrentUserDefault(),
        read_only=True)

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]

    def validate_following(self, value):
        if not isinstance(value, User):
            raise serializers.ValidationError('Имя задано неверно.')
        if self.context.get('request').user.id == value.id:
            raise serializers.ValidationError(
                'Нельза оформить подписку на себя.')
        return value


class RecipesListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TempFollowSerializer(CustomUserSerializer):
    recipes = RecipesListSerializer(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()
