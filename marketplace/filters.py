from django_filters import rest_framework as filters, DateTimeFromToRangeFilter
from rest_framework.filters import SearchFilter, BaseFilterBackend

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


class IsOwnerOrAdminFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their own objects and allows admins to see all objects.
    """
    def filter_queryset(self, request, queryset, view):
        if request.user.is_staff:
            return queryset
        else:
            return queryset.filter(creator=request.user)
