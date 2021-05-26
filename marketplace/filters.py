from django_filters import rest_framework as filters, DateFromToRangeFilter

from marketplace.models import Product


class ProductFilter(filters.FilterSet):
    """Фильтры для товаров."""

    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['min_price', 'max_price']
