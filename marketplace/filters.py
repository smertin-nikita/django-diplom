from django_filters import rest_framework as filters, DateFromToRangeFilter

from marketplace.models import Product


class ProductFilter(filters.FilterSet):
    """Фильтры для товаров."""

    class Meta:
        model = Product
        fields = {
            'price': ['lte', 'gte'],
        }
