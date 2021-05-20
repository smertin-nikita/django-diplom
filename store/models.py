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



