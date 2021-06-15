import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """ Фикстура для клиента API. """
    return APIClient()


@pytest.fixture
def api_auth_admin():
    """ Фикстура для авторизованного как админ клиента API. """

    api_client = APIClient()
    user = baker.make(get_user_model(), is_staff=True)
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return api_client


@pytest.fixture
def api_auth_client():
    """ Фикстура для авторизованного клиента API. """

    api_client = APIClient()
    user = baker.make(get_user_model(), is_staff=False)
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return api_client


@pytest.fixture
def api_auth_another_client():
    """ Фикстура для авторизованного клиента API. """

    api_client = APIClient()
    user = baker.make(get_user_model(), is_staff=False)
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return api_client


@pytest.fixture
def product_factory():
    """ Фабрика для товаров. """
    def func(**kwargs):
        return baker.make('product', **kwargs)

    return func


@pytest.fixture
def order_factory():
    """ Фабрика для заказов. """
    def func(**kwargs):
        return baker.make('order', make_m2m=True, **kwargs)

    return func


@pytest.fixture
def product_ids_factory():
    """ Фабрика для позиций в заказе. """
    def func(**kwargs):
        quantity = kwargs.pop('quantity', None)
        products = kwargs.pop('products', None) or baker.make('product', **kwargs)
        if not isinstance(products, list):
            products = [products]

        if quantity:
            return [{'product_id': obj.id, 'quantity': quantity} for obj in products]
        else:
            return [{'product_id': obj.id} for obj in products]

    return func


@pytest.fixture
def user_factory():
    """ Фабрика для пользователей. """
    def func(**kwargs):
        return baker.make(get_user_model(), **kwargs)

    return func


@pytest.fixture
def review_factory():
    """ Фабрика для отзывов. """
    def func(**kwargs):
        return baker.make('review', **kwargs)

    return func


@pytest.fixture
def collection_factory():
    """ Фабрика для подборок. """
    def func(**kwargs):
        return baker.make('collection', make_m2m=True, **kwargs)

    return func


