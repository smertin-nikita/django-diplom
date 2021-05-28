from django.contrib.auth import get_user_model
from rest_framework import serializers

from marketplace.models import Product, Review, Order


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class ProductSerializer(serializers.ModelSerializer):
    """Serializer для товара."""

    class Meta:
        model = Product
        fields = ('id', 'title', 'description', 'price', 'created_at', )


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer для отзыва."""

    # TODO Как лучше сереализовать создателя отзыва?
    #  Лучше сохранять его как json c данными о пользователе
    # creator = UserSerializer(
    #     read_only=True
    # )
    # TODO Или сохранять только id пользователя?
    creator = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'creator', 'product', 'text', 'mark', 'created_at', )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['creator', 'product']
            )
        ]

    def create(self, validated_data):
        """Метод для создания"""

        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    """Serializer для заказа."""

    # creator = UserSerializer(
    #     read_only=True,
    # )

    creator = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'status', 'creator', 'amount', 'created_at', 'products', )

    def create(self, validated_data):
        """Метод для создания"""

        validated_data["creator"] = self.context["request"].user
        # todo Как и где считать сумму заказа

        return super().create(validated_data)


class CollectionSerializer(serializers.ModelSerializer):
    """Serializer для подборки товаров."""

    class Meta:
        model = Order
        fields = ('id', 'title', 'text', 'created_at', )


