from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from marketplace.models import Product, Review


class UserSerializer(ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class ProductSerializer(ModelSerializer):
    """Serializer для товара."""

    user = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Product
        fields = ('id', 'title', 'description', 'price', 'created_at', )


class ReviewSerializer(ModelSerializer):
    """Serializer для отзыва."""

    user = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'author', 'product', 'text', 'mark', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""

        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        # todo ПРоверить что приходит
        creator = self.context['request'].user
        product = data['product']

        if Review.objects.filter(creator=creator, product=product).exist():
            raise ValidationError("Вы не можете оставлять более одного отзыва.")

        return data

