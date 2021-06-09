from django_filters import rest_framework as filters, DateTimeFromToRangeFilter
from rest_framework.filters import SearchFilter

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

    created_at = DateTimeFromToRangeFilter()

    class Meta:
        model = Review
        fields = ['creator', 'product', 'created_at']


class OrderProductSearchFilter(SearchFilter):
    def get_search_fields(self, view, request):
        if request.query_params.get('product_id'):
            return ['=order_positions__product__id']
        return super().get_search_fields(view, request)


class OrderFilter(filters.FilterSet):
    """Фильтры для товаров."""

    created_at = DateTimeFromToRangeFilter()
    updated_at = DateTimeFromToRangeFilter()

    class Meta:
        model = Order
        fields = ['status', 'created_at', 'updated_at', 'amount']
