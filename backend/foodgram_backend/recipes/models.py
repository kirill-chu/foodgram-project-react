from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class MeasurementUnit(models.Model):
    """Модель единиц измерения."""

    unit_name = models.CharField(
        verbose_name="Единица измерения", max_length=15, unique=True)

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'
        ordering = ['id']

    def __str__(self):
        return f'{self.id}: {self.slug} {self.name}'


class Ingredient(models.Model):
    """Модель ингридиентов."""

    name = models.CharField(verbose_name="Название", max_length=75)
    measurement_unit = models.ForeignKey(
        MeasurementUnit, verbose_name="Единица измерения",
        on_delete=models.CASCADE, related_name='MeasurementUnit')

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.id}: {self.name}'


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(verbose_name='Тег', max_length=50)
    slug = models.SlugField(verbose_name='Slug', unique=True, max_length=50)
    color = models.CharField(verbose_name='Цвет', max_length=16)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return f'{self.id}: {self.name} {self.slug}'


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE,
        related_name='recipes')
    name = models.CharField(verbose_name='Название', max_length=100)
    image = models.ImageField(
        verbose_name='Картинка', upload_to='recipes/images/')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe', related_name='ingredient')
    tags = models.ManyToManyField(
        Tag, through='TagRecipe', related_name='tag')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(settings.MIN_VALUE),
            MaxValueValidator(settings.MAX_VALUE)])

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return f'{self.id}: {self.name}'


class TagRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE)
    tag = models.ForeignKey(
        Tag, verbose_name='Тег', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тег и Рецепт'
        verbose_name_plural = 'Теги и Рцепты'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unique_recipe_tag'
            )
        ]

    def __str__(self):
        return f'{self.id}: {self.recipe.name} {self.tag.name}'


class IngredientRecipe(models.Model):
    """Модель для связи многие ко многим. Ингридиенты и рецепты."""

    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='Ингридиент', on_delete=models.CASCADE)

    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(settings.MIN_VALUE),
            MaxValueValidator(settings.MAX_VALUE)])

    class Meta:
        verbose_name = 'Ингридиент и Рецепт'
        verbose_name_plural = 'Ингридиеты и Рцепты'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name} {self.ingredient.name} {self.amount}'


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
                fields=['user', 'following'],
                name='unique_follow')
        ]
        ordering = ['following__username']

    def __str__(self):
        return f'{self.user.username} {self.following.username}'


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
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.id}: {self.user.username} {self.recipe.name}'


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
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.id}: {self.user}: {self.recipe}'
