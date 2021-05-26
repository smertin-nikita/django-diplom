from rest_framework import filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser, AND
from rest_framework.viewsets import ModelViewSet

from marketplace.filters import ProductFilter
from marketplace.models import Product, Review, Order, Collection
from marketplace.permissions import IsOwnerOrReadOnly, IsOwnerUser, OnlyEditToOrderStatus
from marketplace.serializers import CollectionSerializer, OrderSerializer, ProductSerializer, ReviewSerializer


class ProductViewSet(ModelViewSet):
    """ Viewset для товаров. """

    queryset = Product.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly | IsAdminUser]
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
    filterset_class = ProductFilter


class ReviewViewSet(ModelViewSet):
    """ Viewset для отзывов. """

    queryset = Review.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly | IsOwnerOrReadOnly]
    serializer_class = ReviewSerializer
    # filterset_class = ReviewFilter


class OrderViewSet(ModelViewSet):
    """ Viewset для заказов. """

    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated & IsOwnerUser]
    serializer_class = OrderSerializer
    # filterset_class = OrderFilter

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["partial_update"]:
            return [AND(OnlyEditToOrderStatus(), IsAdminUser())]
        return []


class CollectionViewSet(ModelViewSet):
    """ Viewset для подборок. """

    queryset = Collection.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly | IsAdminUser]
    serializer_class = CollectionSerializer
    # filterset_class = CollectionFilter
