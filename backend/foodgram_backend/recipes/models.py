from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MeasurementUnit(models.Model):
    """Модель единиц измерения."""

    unit_name = models.CharField(
        verbose_name="Единица измерения", max_length=15, unique=True)

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'


class Ingredient(models.Model):
    """Модель ингридиентов."""

    name = models.CharField(verbose_name="Название", max_length=50)
    measurement_unit = models.ForeignKey(
        MeasurementUnit, verbose_name="Единица измерения",
        on_delete=models.CASCADE, related_name='MeasurementUnit')

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(verbose_name='Тег', max_length=50)
    slug = models.SlugField(verbose_name='Slug', unique=True, max_length=50)
    color = models.CharField(verbose_name='Цвет', max_length=16)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE,
        related_name='recipes')
    name = models.CharField(verbose_name='Название', max_length=100)
    image = models.ImageField(
        verbose_name='Картинка', upload_to='recipes/images/')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe')
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class TagRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE)
    tag = models.ForeignKey(
        Tag, verbose_name='Тег', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тег и Рецепт'
        verbose_name_plural = 'Теги и Рцепты'


class IngredientRecipe(models.Model):
    """Модель для связи многие ко многим. Ингридиенты и рецепты."""

    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='Ингридиент', on_delete=models.CASCADE)

    amount = models.FloatField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингридиент и Рецепт'
        verbose_name_plural = 'Ингридиеты и Рцепты'


class Follow(models.Model):
    """Подписки."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='Подписчик')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_follow')
        ]


class Favorite(models.Model):
    """Избранное."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorite',
        verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite')
        ]


class ShoppingCart(models.Model):
    """Крзина для покупок."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
