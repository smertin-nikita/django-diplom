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
        fields = ('id', 'title', 'description', 'price', 'created_at', 'updated_at',)


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer для отзыва."""
    partial = True
    creator = UserSerializer(
        read_only=True
    )
    product = ProductSerializer(
        read_only=True
    )
    product_id = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Product.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'creator', 'product', 'product_id', 'text', 'mark', 'created_at', 'updated_at', )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.only('creator', 'product_id'),
                fields=['creator', 'product_id']
            )
        ]

    def to_internal_value(self, data):

        # todo Только при правильно выставленных permission, так как обновлять создателя отзыва нельзя.
        #  eсли делать в методе create не пройдет валидация на required field в UniqueTogetherValidator.
        ret = super().to_internal_value(data)
        ret['creator'] = self.context["request"].user

        return ret

    def create(self, validated_data):
        """Метод для создания"""

        # todo Не знаю как правильно делать запросы. Либо отправлять только id сущности(product_id)
        #  либо всю сущность(product). Решил сделать только id
        #  Костыль чтобы при записи требовался только product_id, а в отображении был instance product
        product = validated_data['product_id']
        validated_data['product_id'] = product.id
        validated_data['product'] = product

        review = Review.objects.create(**validated_data)

        return review

    def update(self, instance, validated_data):
        """Метод для обновления"""

        # todo Если в бизнес логике можно менять продукт в отзыве.
        if validated_data.get('product_id'):
            if Review.objects.filter(creator=validated_data['creator'], product=validated_data['product_id']).exists():
                raise serializers.ValidationError(
                    {"non_field_errors": ["The fields creator, product_id must make a unique set."]}
                )
            else:
                product = validated_data['product_id']
                validated_data['product_id'] = product.id
                validated_data['product'] = product
                return super().update(instance, validated_data)

        return super().update(instance, validated_data)


class ProductOrderSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(required=True, queryset=Product.objects.all(), write_only=True)

    class Meta:
        model = ProductOrder
        fields = ('product', 'quantity', 'product_id',)


class OrderSerializer(serializers.ModelSerializer):
    """Serializer для заказа."""

    MAX_AMOUNT_VALUE = 100000000
    MIN_AMOUNT_VALUE = 1

    creator = UserSerializer(
        read_only=True,
    )

    positions = ProductOrderSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'amount', 'positions', 'status', 'creator', 'created_at', 'updated_at', )
        extra_kwargs = {
            'status': {'read_only': True},
            'amount': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def __init__(self, *args, **kwargs):
        # Check if we're updating.
        # updating = "instance" in kwargs and "data" in kwargs

        # Make sure the original initialization is done first.
        super().__init__(*args, **kwargs)

        # If we're updating, make the positions field read only and status not read only.
        if self.context['request'].method == 'PUT' or self.context['request'].method == 'PATCH':
            self.fields['positions'].read_only = True
            self.fields['status'].read_only = False

    def create(self, validated_data):
        """Метод для создания"""

        validated_data['creator'] = self.context["request"].user

        positions = validated_data.pop('positions')
        order = Order.objects.create(**validated_data)

        for order_data in positions:
            order_data['product'] = order_data.pop('product_id')
            ProductOrder.objects.create(order=order, **order_data)

        return order

    def validate(self, data):
        """ Calculate and validate amount of order."""

        if self.context["request"].method == "POST":
            positions = data.get('positions')
            data['amount'] = sum(order_data['product_id'].price * order_data.get('quantity', 1) for order_data in positions)
            # min and max possible amount of order
            if data['amount'] < self.MIN_AMOUNT_VALUE:
                raise serializers.ValidationError(f"The amount cannot be less than {self.MIN_AMOUNT_VALUE}")
            if data['amount'] > self.MAX_AMOUNT_VALUE:
                raise serializers.ValidationError(f"The amount cannot be more than {self.MAX_AMOUNT_VALUE}")

        return data

    def validate_positions(self, data):
        if not len(data):
            raise serializers.ValidationError({'positions': 'The field cannot be an empty list'})

        return data


class CollectionSerializer(serializers.ModelSerializer):
    """Serializer для подборки товаров."""

    class Meta:
        model = Order
        fields = ('id', 'title', 'text', 'created_at', 'updated_at', )


