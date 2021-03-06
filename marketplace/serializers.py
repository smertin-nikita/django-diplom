from django.contrib.auth import get_user_model
from rest_framework import serializers

from marketplace.models import Product, Review, Order, OrderProduct, Collection, CollectionProduct


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
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


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
        fields = ('id', 'text', 'mark', 'created_at', 'updated_at', 'creator', 'product', 'product_id',)
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.only('creator', 'product_id'),
                fields=['creator', 'product_id']
            )
        ]

    def __init__(self, *args, **kwargs):

        # Make sure the original initialization is done first.
        super().__init__(*args, **kwargs)

        # If we're updating, make the positions field read only and status not read only.
        if self.context['request'].method in ['PUT', 'PATCH']:
            self.fields['creator'].read_only = True

    def to_internal_value(self, data):

        # TODO eсли делать в методе create не пройдет валидация на required field в UniqueTogetherValidator.
        ret = super().to_internal_value(data)
        ret['creator'] = self.context["request"].user

        return ret

    def create(self, validated_data):
        """Метод для создания"""

        validated_data['product'] = validated_data.pop('product_id')
        return Review.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Метод для обновления"""
        product_id = validated_data.pop('product_id', False)
        if product_id:
            validated_data['product'] = product_id
        return super().update(instance, validated_data)

    def validate(self, data):
        """ Calculate and validate amount of order."""

        if self.context["request"].method in ['PUT', 'PATCH']:
            if data.get('product_id'):
                if Review.objects.filter(creator=data['creator'],
                                         product=data['product_id']).exists():
                    raise serializers.ValidationError(
                        {"non_field_errors": ["The fields creator, product_id must make a unique set."]}
                    )

        return data


class ProductOrderSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(required=True, queryset=Product.objects.all(), write_only=True)

    class Meta:
        model = OrderProduct
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
        fields = ('id', 'amount',  'status', 'created_at', 'updated_at', 'creator', 'positions',)
        extra_kwargs = {
            'status': {'read_only': True},
            'amount': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def __init__(self, *args, **kwargs):

        # Make sure the original initialization is done first.
        super().__init__(*args, **kwargs)

        # If we're updating, make the positions field read only and status not read only.
        if self.context['request'].method in ['PUT', 'PATCH']:
            self.fields['positions'].read_only = True
            self.fields['status'].read_only = False

    def create(self, validated_data):
        """Метод для создания"""

        validated_data['creator'] = self.context["request"].user

        positions = validated_data.pop('positions')
        order = Order.objects.create(**validated_data)

        for item in positions:
            item['product'] = item.pop('product_id')
            OrderProduct.objects.create(order=order, **item)

        return order

    def validate(self, data):
        """Calculate and validate amount of order."""

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
        """Checks positions for empty list."""
        if not len(data):
            raise serializers.ValidationError(['The field cannot be an empty list'])

        return data


class CollectionProductSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(required=True, queryset=Product.objects.all(), write_only=True)

    class Meta:
        model = CollectionProduct
        fields = ('product', 'product_id',)


class CollectionSerializer(serializers.ModelSerializer):
    """Serializer для подборки товаров."""

    products = CollectionProductSerializer(many=True)

    class Meta:
        model = Collection
        fields = ('id', 'title', 'text', 'created_at', 'updated_at', 'products',)
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def create(self, validated_data):
        """Метод для создания"""

        products = validated_data.pop('products')
        collection = Collection.objects.create(**validated_data)

        for item in products:
            CollectionProduct.objects.create(collection=collection, product=item.pop('product_id'))

        return collection

    def update(self, instance, validated_data):
        """Метод для создания"""

        instance_products = CollectionProduct.objects.filter(collection=instance)
        data_products = {}
        for item in validated_data.pop('products'):
            product = item.get('product_id', False)
            if not product:
                raise serializers.ValidationError({"products": [{"product_id": ["This field is required."]}]})
            data_products[product.id] = product

        # Perform creations
        for product_id, product in data_products.items():
            if not instance_products.filter(product=product).exists():
                CollectionProduct.objects.create(collection=instance, product=product)

        # Perform deletions.
        for obj in instance_products:
            if obj.product_id not in data_products:
                obj.delete()

        return super().update(instance, validated_data)

    def validate_products(self, data):
        """Checks products for empty list"""
        if not len(data):
            raise serializers.ValidationError(['The field cannot be an empty list'])

        return data


