from django.db import models

from website import settings


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
        verbose_name='Дана обновления'
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
        verbose_name='Описание'
    )

    price = models.DecimalField(
        null=False,
        blank=False,
        max_digits=8,
        decimal_places=2,
        verbose_name='Цена'
    )


class Review(DateInfo):
    """ Отзывы """

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name='Пользователь'
    )

    # Todo удалять ли отзывы если продукт удален или Продукт не удаляется, а просто не в наличии
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name='Товар'
    )

    text = models.TextField(
        null=False,
        blank=True,
        verbose_name='Текст'
    )

     mark = models.TextChoices()



