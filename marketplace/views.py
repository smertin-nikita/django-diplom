from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from marketplace.models import Product, Review


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    # serializer_class = ProductSerializer
    # filterset_class = ProductFilter

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsStaffOrReadOnly()]
        return []


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    # serializer_class = ReviewSerializer
    # filterset_class = ReviewFilter

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return []

