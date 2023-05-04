from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserSerializer

from recipes.models import Ingredient, Tag

User = get_user_model()


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
        return False


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериалайзер для Ингридиентов."""

    measurement_unit = serializers.SlugRelatedField(
        read_only=True, slug_field='unit_name')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для Тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
