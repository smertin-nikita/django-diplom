from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser, OR
from rest_framework.viewsets import ModelViewSet

from marketplace.filters import ProductFilter, ReviewFilter, OrderFilter
from marketplace.models import Product, Review, Order, Collection
from marketplace.permissions import IsOwnerUser, OnlyAdminEditToOrderStatus, IsAdminUserOrReadOnly
from marketplace.serializers import CollectionSerializer, OrderSerializer, ProductSerializer, ReviewSerializer


class ProductViewSet(ModelViewSet):
    """ Viewset для товаров. """

    queryset = Product.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly & IsAdminUserOrReadOnly]
    serializer_class = ProductSerializer
    # Search filter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description']

    filterset_class = ProductFilter


class ReviewViewSet(ModelViewSet):
    """ Viewset для отзывов. """

    queryset = Review.objects.select_related('creator', 'product')
    permission_classes = [IsAuthenticatedOrReadOnly & IsAdminUserOrReadOnly]
    serializer_class = ReviewSerializer

    filterset_class = ReviewFilter

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["partial_update", 'delete', 'update']:
            return [OR(IsOwnerUser(), IsAdminUser())]

        return []


class OrderViewSet(ModelViewSet):
    """ Viewset для заказов. """

    queryset = Order.objects.all().prefetch_related('order_positions')
    permission_classes = [IsAuthenticated & IsOwnerUser]
    serializer_class = OrderSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['amount', ]

    filterset_class = OrderFilter

    def get_queryset(self):
        """queryset с заказами только для создателя или для админа c фильтрацией по продукту из позиции"""

        filter_params = {}

        # фильтрация для продукта из позиции
        product_id = self.request.query_params.get('product_id')
        if product_id is not None:
            filter_params = {'order_positions__product__id': product_id}

        user = self.request.user
        if user.is_staff:
            return super().get_queryset().filter(**filter_params)

        return user.order_set.filter(**filter_params)

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["partial_update"]:
            return [OnlyAdminEditToOrderStatus()]

        return []


class CollectionViewSet(ModelViewSet):
    """ Viewset для подборок. """

    queryset = Collection.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly | IsAdminUser]
    serializer_class = CollectionSerializer
