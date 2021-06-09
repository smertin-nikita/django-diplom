from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
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
    product_id = serializers.PrimaryKeyRelatedField(required=True, queryset=Product.objects.all())

    class Meta:
        model = Review
        fields = ('id', 'creator', 'product', 'product_id', 'text', 'mark', 'created_at', 'updated_at', )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
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

        review = Review.objects.create(product=product, **validated_data)

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
    product_id = serializers.PrimaryKeyRelatedField(required=True, queryset=Product.objects.all())

    class Meta:
        model = ProductOrder
        fields = ('product', 'quantity', 'product_id',)

    # def to_internal_value(self, data):
    #
    #     ret = super().to_internal_value(data)
    #     #
    #     #
    #     # try:
    #     #     ret['product'] = Product.objects.get(id=data['product'])
    #     # except ObjectDoesNotExist:
    #     #     raise serializers.ValidationError({"product": 'does not exist.'})
    #
    #     ret['creator'] = self.context["request"].user
    #
    #     return ret


class OrderSerializer(serializers.ModelSerializer):
    """Serializer для заказа."""

    creator = UserSerializer(
        read_only=True,
    )

    # creator = serializers.PrimaryKeyRelatedField(
    #     read_only=True,
    #     default=serializers.CurrentUserDefault()
    # )

    order_positions = ProductOrderSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'amount', 'order_positions', 'status', 'creator', 'created_at', 'updated_at', )
        extra_kwargs = {'amount': {'required': False}}

    def to_internal_value(self, data):

        ret = super().to_internal_value(data)
        ret['creator'] = self.context["request"].user

        return ret

    def create(self, validated_data):
        """Метод для создания"""

        order_positions = validated_data.pop('order_positions')
        amount = sum(order_data['product_id'].price * order_data['quantity'] for order_data in order_positions)
        order = Order.objects.create(creator=validated_data['creator'], amount=amount)
        for order_data in order_positions:
            product = order_data['product_id']
            order_data['product_id'] = product.id
            ProductOrder.objects.create(order=order, **order_data)
        return order

    def validate(self, data):
        if not len(data['order_positions']):
            raise serializers.ValidationError({'product_id': 'The field is required'})

        return data

class CollectionSerializer(serializers.ModelSerializer):
    """Serializer для подборки товаров."""

    class Meta:
        model = Order
        fields = ('id', 'title', 'text', 'created_at', 'updated_at', )


