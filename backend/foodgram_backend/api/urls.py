from django.urls import include, path

from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewset

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserViewset)
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('tags', TagViewSet)
router_v1.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
