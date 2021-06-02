from django_filters import rest_framework as filters, DateFromToRangeFilter

from marketplace.models import Product, Review, Order


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


class OrderFilter(filters.FilterSet):
    """Фильтры для товаров."""

    created_at = DateFromToRangeFilter()
    updated_at = DateFromToRangeFilter()

    class Meta:
        model = Order
        fields = ['status', 'created_at', 'updated_at', 'order_positions__product']
        # fields = {'amount': ['lte', 'gte']}
