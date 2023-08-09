import django_filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(field_name='tags__slug',
                                     method='filter_tags')
    is_favorited = django_filters.NumberFilter(
        field_name='is_favorited', method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        field_name='is_in_shopping_cart', method='filter_is_in_shopping_cart')

    def filter_tags(self, queryset, name, value):
        captured_value = self.request.GET.getlist('tags')
        if captured_value:
            return queryset.filter(tags__slug__in=captured_value).distinct()
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user).distinct()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(
                shopping_cart__user=self.request.user).distinct()
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'is_favorited')
