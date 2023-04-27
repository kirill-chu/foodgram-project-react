from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserSerializer

User = get_user_model()


class CustomUserCreateSerializer(UserSerializer):
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
