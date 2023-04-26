from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer

User = get_user_model()


class CustomUserCreateSerializer(UserSerializer):
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )


class SignupSerializer(serializers.ModelSerializer):
    """Сериалайзер для регситрации пользователя."""

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                f'Запрещено использовать {value} в качестве имени'
            )
        return value

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер просмотра пользователя."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')
