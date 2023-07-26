from django.contrib import admin

from .models import Favorite, Follow, IngredientRecipe, Recipe, Tag, TagRecipe

admin.site.register(Tag)
# admin.site.register(Recipe)
admin.site.register(TagRecipe)
admin.site.register(IngredientRecipe)
admin.site.register(Follow)
admin.site.register(Favorite)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'author', 'name', 'image', 'text',
        'cooking_time')
    search_fields = ('name',)
    list_filter = ('tags',)


admin.site.register(Recipe, RecipeAdmin)
