import django_filters

from recipes.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ['tags']


class ShopFilter(django_filters.FilterSet):

    class Meta:
        model = Recipe
        fields = ['is_in_shopping_cart']
