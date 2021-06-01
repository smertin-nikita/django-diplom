from django.contrib.auth import get_user_model
from rest_framework import serializers

from marketplace.models import Product, Review, Order, ProductOrder


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


class ProductOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductOrder
        fields = ('product', 'quantity',)


class OrderSerializer(serializers.ModelSerializer):
    """Serializer для заказа."""

    # creator = UserSerializer(
    #     read_only=True,
    # )

    creator = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    # TODO Аналогично как с полем creator
    #  сделать вложенность или работать только с id
    products = ProductSerializer(many=True, read_only=True)
    order_positions = ProductOrderSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'products', 'order_positions', 'status', 'creator', 'created_at',]

    def create(self, validated_data):
        """Метод для создания"""

        creator = self.context["request"].user

        order_positions = validated_data.pop('order_positions')
        amount = sum(order_data['product'].price * order_data['quantity'] for order_data in order_positions)
        order = Order.objects.create(creator=creator, amount=amount)
        for order_data in order_positions:
            ProductOrder.objects.create(order=order, **order_data)
        return order


class CollectionSerializer(serializers.ModelSerializer):
    """Serializer для подборки товаров."""

    class Meta:
        model = Order
        fields = ('id', 'title', 'text', 'created_at', )


