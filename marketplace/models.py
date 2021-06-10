from django.conf import settings
from django.contrib.postgres import validators
from django.db import models


class DateInfo(models.Model):
    """ Общая информация о времени создании и обновления сущностей"""

    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )


class Product(DateInfo):
    """ Товар """

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    title = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        verbose_name='Наименование'
    )

    description = models.TextField(
        null=False,
        blank=True,
        default='',
        verbose_name='Описание'
    )

    price = models.DecimalField(
        null=False,
        blank=False,
        max_digits=9,
        decimal_places=2,
        verbose_name='Цена',
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(100000)]
    )

    def __str__(self):
        return self.title


class Review(DateInfo):
    """ Отзывы """

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('creator', 'product',)

    class ProductMarks(models.IntegerChoices):
        """ Оценка товара """

        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        blank=False,
        null=False,
        verbose_name='Пользователь'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name='Товар',
        related_name='reviews'
    )

    text = models.TextField(
        null=False,
        blank=True,
        default='',
        verbose_name='Текст'
    )

    mark = models.IntegerField(
        choices=ProductMarks.choices,
        null=False,
        blank=False
    )


class ProductOrder(models.Model):
    """ Позиции. Промежуточная таблица между товаром и заказом """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='positions')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_positions')
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[validators.MinValueValidator(1), validators.MaxValueValidator(10000)]
    )


class Order(DateInfo):
    """ Заказы. """

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    class OrderStatus(models.TextChoices):
        """ Статус заказа """

        NEW = 'NEW', 'Новый'
        IN_PROGRESS = 'IN_PROGRESS', 'В процессе'
        DONE = 'DONE', 'Выполнен'

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name='Пользователь'
    )

    products = models.ManyToManyField(
        Product, through=ProductOrder,
        verbose_name='Позиции',
        blank=False
    )

    amount = models.DecimalField(
        null=False,
        blank=True,
        default=0,
        max_digits=12,
        decimal_places=2,
        verbose_name='Сумма',
    )

    status = models.TextField(
        choices=OrderStatus.choices,
        verbose_name='Статус',
        default=OrderStatus.NEW
    )


class Collection(DateInfo):
    """ Коллекция товаров """

    class Meta:
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'

    title = models.CharField(
        null=False,
        blank=False,
        max_length=255
    )

    text = models.TextField(
        null=False,
        blank=True,
        default=''
    )

    products = models.ManyToManyField(
        Product,
        related_name='collections'
    )

    def __str__(self):
        return self.title



