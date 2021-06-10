from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser, OR, AND
from rest_framework.viewsets import ModelViewSet

from marketplace.filters import ProductFilter, ReviewFilter, OrderFilter, IsOwnerOrAdminFilterBackend
from marketplace.models import Product, Review, Order, Collection, ProductOrder
from marketplace.permissions import OnlyAdminEditToOrderStatus, IsAdminUserOrReadOnly, IsOwnerUser, IsOwnerOrAdminUser
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
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ReviewSerializer

    filterset_class = ReviewFilter

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["partial_update", 'update']:
            return [IsOwnerUser()]
        elif self.action == 'destroy':
            return [IsOwnerOrAdminUser()]
        else:
            return super(ReviewViewSet, self).get_permissions()


class OrderViewSet(ModelViewSet):
    """ Viewset для заказов. """

    productorder_set = ProductOrder.objects.select_related('product')
    queryset = Order.objects.prefetch_related(Prefetch('order_positions', queryset=productorder_set))
    permission_classes = [IsAuthenticated & IsOwnerOrAdminUser]
    serializer_class = OrderSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, IsOwnerOrAdminFilterBackend]
    ordering_fields = ['amount', ]

    filterset_class = OrderFilter

    # def get_queryset(self):
    #     """queryset с заказами только для создателя или для админа c фильтрацией по продукту из позиции"""
    #
    #     self.check_object_permissions(self.request, self.request.user)
    #
    #     filter_params = {}
    #
    #     # фильтрация для продукта из позиции
    #     product_id = self.request.query_params.get('product_id')
    #     if product_id is not None:
    #         filter_params = {'order_positions__product__id': product_id}
    #
    #     return user.order_set.filter(**filter_params)

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action == "create":
            return [IsAuthenticated()]
        elif self.action in ["partial_update", "update"]:
            return [OnlyAdminEditToOrderStatus()]
        else:
            return super(OrderViewSet, self).get_permissions()


class CollectionViewSet(ModelViewSet):
    """ Viewset для подборок. """

    queryset = Collection.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly | IsAdminUser]
    serializer_class = CollectionSerializer
