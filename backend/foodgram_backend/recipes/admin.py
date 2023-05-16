from django.contrib import admin

from .models import Tag, Recipe, TagRecipe, IngredientRecipe, Follow

admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(TagRecipe)
admin.site.register(IngredientRecipe)
admin.site.register(Follow)
