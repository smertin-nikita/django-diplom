import decimal
import random

import pytest
from pytest_django.fixtures import admin_user, django_user_model, client
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, \
    HTTP_403_FORBIDDEN

from website import settings


@pytest.mark.django_db
def test_retrieve_product(api_client, product_factory):

    # arrange
    product = product_factory()

    url = reverse("products-detail", kwargs={'pk': product.id})

    # act
    resp = api_client.get(url)

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 6  # fields count
    assert resp_json['id'] == product.id
    assert resp_json['title'] == product.title
    assert resp_json['description'] == product.description
    assert decimal.Decimal(resp_json['price']) == product.price


@pytest.mark.django_db
def test_list_products(api_client, product_factory):

    # arrange
    products = product_factory(_quantity=10)

    url = reverse("products-list")

    # act
    resp = api_client.get(url)

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == len(products)
    for i, item in enumerate(resp_json):
        assert item['id'] == products[i].id
        assert 'title' in item
        assert item['title'] == products[i].title
        assert 'description' in item
        assert item['description'] == products[i].description
        assert 'price' in item
        assert decimal.Decimal(item['price']) == products[i].price


@pytest.mark.django_db
def test_filter_price_products(api_client, product_factory):
    # arrange
    test_price = decimal.Decimal(random.randrange(99999999999))/100
    products = product_factory(_quantity=10)

    url = reverse("products-list")

    # act
    resp = api_client.get(url, {'price__gte': test_price})

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    for item in resp_json:
        assert decimal.Decimal(item['price']) >= test_price

    # act
    resp = api_client.get(url, {'price__lte': test_price})

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    for item in resp_json:
        assert decimal.Decimal(item['price']) <= test_price


@pytest.mark.django_db
def test_filter_search_products(api_client, product_factory):
    # arrange
    product = product_factory()
    product_factory()

    url = reverse("products-list")

    # act test title
    resp = api_client.get(url, {'search': product.title})

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 1
    test_product = resp_json[0]
    assert test_product['id'] == product.id
    assert test_product['title'] == product.title

    #Todo придумать тест для фильтр поиска по описанию


@pytest.mark.parametrize(
    ['oauth', "is_staff", "price", "expected_status"],
    (
        (True, True, "400", HTTP_201_CREATED),
        (True, True, "-100", HTTP_400_BAD_REQUEST),
        (True, True, "100000000", HTTP_400_BAD_REQUEST),
        (True, False, "400", HTTP_403_FORBIDDEN),
        (False, False, "400", HTTP_401_UNAUTHORIZED),
    )
)
@pytest.mark.django_db
def test_create_product(api_client, oauth, is_staff, price, expected_status, user_factory):

    if oauth:
        user = user_factory(is_staff=is_staff)
        token = Token.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    # arrange
    payload = {
        'title': 'test',
        'price': price
    }
    url = reverse("products-list")

    # act
    resp = api_client.post(url, payload)

    # assert

    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json


@pytest.mark.django_db
def test_update_product(api_client, product_factory, user_factory):
    # arrange

    user = user_factory(is_staff=True)
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    product = product_factory()

    payload = {
        'title': 'test',
        'price': 500,
        'description': 'any text',
    }
    url = reverse("products-detail", kwargs={'pk': product.id})

    # act
    resp = api_client.patch(url, payload)

    # assert

    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 6  # fields count
    assert resp_json['id'] == product.id
    assert 'updated_at' in resp_json

