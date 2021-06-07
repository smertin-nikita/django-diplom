import decimal
import random

import pytest
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK


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
    assert len(resp_json) == 5  # fields count
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
