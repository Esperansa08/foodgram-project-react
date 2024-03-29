from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all())
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)

    def filter_is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_list__user=user)
        return queryset

    def filter_is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorite__user=user)
        return queryset
