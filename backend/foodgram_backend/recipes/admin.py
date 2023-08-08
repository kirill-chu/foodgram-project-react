from django.contrib import admin

from .models import (Favorite, Follow, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag, TagRecipe)

admin.site.register(Tag)
admin.site.register(TagRecipe)
admin.site.register(IngredientRecipe)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'meas_unit')
    list_filter = ('name',)

    def meas_unit(self, obj):
        return obj.measurement_unit.unit_name
    meas_unit.short_description = 'Единица измерения'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'author', 'name', 'image', 'text',
        'cooking_time', 'favorite_count')
    search_fields = ('name',)
    list_filter = ('tags', 'name', 'author')
    inlines = (RecipeIngredientInline,)

    def favorite_count(self, obj):
        return obj.favorite.count()
    favorite_count.short_description = 'В избранных'
