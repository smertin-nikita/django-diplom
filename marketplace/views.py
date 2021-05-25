from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.viewsets import ModelViewSet

from marketplace.models import Product, Review, Order, Collection
from marketplace.permissions import IsOwnerOrReadOnly, IsOwnerUser


class ProductViewSet(ModelViewSet):
    """ Viewset для товаров. """

    queryset = Product.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly | IsAdminUser]
    # serializer_class = ProductSerializer
    # filterset_class = ProductFilter

    # def get_permissions(self):
    #     """Получение прав для действий."""
    #     if self.action in ["create", "update", "partial_update", "destroy"]:
    #         return [IsAuthenticated(), IsStaffOrReadOnly()]
    #     return []


class ReviewViewSet(ModelViewSet):
    """ Viewset для отзывов. """

    queryset = Review.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly | IsOwnerOrReadOnly]
    # serializer_class = ReviewSerializer
    # filterset_class = ReviewFilter


class OrderViewSet(ModelViewSet):
    """ Viewset для заказов. """
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated & IsOwnerUser]
    # serializer_class = OrderSerializer
    # filterset_class = OrderFilter

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["partial_update"]:
            return [, IsOwnerOrReadOnly()]
        return []


class CollectionViewSet(ModelViewSet):
    """ Viewset для подборок. """
    queryset = Collection.objects.all()
    # serializer_class = CollectionSerializer
    # filterset_class = CollectionFilter

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return []