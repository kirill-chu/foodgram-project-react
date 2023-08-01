import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


from recipes.models import (
    Favorite, Follow, Ingredient, IngredientRecipe, Recipe, ShoppingCart, Tag,
    TagRecipe)

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
        if self.context.get('request').user.is_authenticated:
            user = (self.context.get('request').user)
            return obj.following.filter(user=user).exists()
        return False


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

    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit.unit_name')
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    amount = serializers.FloatField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для Ингридиентов."""

    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.FloatField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалейзер для рецептов."""

    author = CustomUserSerializer(read_only=True, many=False)
    ingredients = IngredientRecipeSerializer(
        source='ingredientrecipe_set', read_only=True, many=True)
    tags = TagSerializer(many=True, read_only=True)

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        if self.context.get('request').user.is_authenticated:
            user = (self.context.get('request').user)
            return obj.favorite.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request').user.is_authenticated:
            user = self.context.get('request').user
            return obj.shopping_cart.filter(user=user).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи рецептов."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault())

    ingredients = IngredientRecipeWriteSerializer(
        source='ingredientrecipe_set', many=True)

    image = Base64ImageField(required=True, allow_null=False)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name', 'image', 'text',
                  'cooking_time', 'author')

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        """Метод создания рецепта."""

        ingredients = validated_data.pop('ingredientrecipe_set')

        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(
                id=ingredient.get('ingredient').get('id'))

            IngredientRecipe.objects.create(
                ingredient=current_ingredient,
                amount=ingredient['amount'], recipe=recipe)

        for tag in tags:
            current_tag = Tag.objects.get(id=tag.id)
            TagRecipe.objects.create(tag=current_tag, recipe=recipe)

        return recipe

    def update(self, instance, validated_data):
        """Метод для обновления рецепта."""

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientrecipe_set')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(update_fields=validated_data)

        TagRecipe.objects.filter(recipe=instance).delete()
        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=instance)

        IngredientRecipe.objects.filter(recipe=instance.id).delete()
        for ingredient in ingredients:
            try:
                IngredientRecipe.objects.create(
                    ingredient_id=ingredient.get('ingredient').get('id'),
                    recipe=instance, amount=ingredient.get('amount'))
            except IntegrityError:
                msg = (
                    {'detail': 'Ингредиент c id: '
                     f'{ingredient.get("ingredient").get("id")} не найден!'})
                raise serializers.ValidationError(msg)
        return instance


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


class GetRecipe:
    requires_context = True

    def __call__(self, serializer_field):
        context = serializer_field.context['request'].parser_context
        return get_object_or_404(Recipe, id=context.get('kwargs').get('id'))


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""

    name = serializers.SlugRelatedField(
        slug_field='name', default=GetRecipe(), read_only=True)
    id = serializers.ReadOnlyField(source='recipe_id')
    image = serializers.SerializerMethodField()
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.recipe.image)


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для продуктовой корзины."""

    # user = serializers.SlugRelatedField(
    #    slug_field='username', default=serializers.CurrentUserDefault(),
    #    queryset=User.objects.all(), write_only=True)
    
    name = serializers.SlugRelatedField(
        slug_field='name', default=GetRecipe(), read_only=True)
    id = serializers.ReadOnlyField(source='recipe_id')
    image = serializers.SerializerMethodField(read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.recipe.image)


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Сеирализатор для смены пароля."""

    current_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True)
    new_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        exclude = ('id', 'password', 'email', 'username', 'first_name',
                   'last_name')
