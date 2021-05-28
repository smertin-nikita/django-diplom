from django_filters import rest_framework as filters, DateFromToRangeFilter

from marketplace.models import Product, Review


class ProductFilter(filters.FilterSet):
    """Фильтры для товаров."""

    class Meta:
        model = Product
        fields = {
            'price': ['lte', 'gte'],
        }


class ReviewFilter(filters.FilterSet):
    """Фильтры для товаров."""

    created_at = DateFromToRangeFilter()

    class Meta:
        model = Review
        fields = ['creator', 'product', 'created_at']