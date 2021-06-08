import decimal
import random

import pytest
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, \
    HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT


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
        assert item['title'] == products[i].title
        assert item['description'] == products[i].description
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
    product = product_factory(description='1')
    product_factory(description='2')

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

    # act test description
    resp = api_client.get(url, {'search': product.description})

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 1
    test_product = resp_json[0]
    assert test_product['id'] == product.id
    assert test_product['description'] == product.description


@pytest.mark.django_db
def test_user_permissions_for_product(api_client, api_auth_client, api_auth_admin, product_factory):

    payload = {
        'title': 'test',
        'price': '500'
    }
    # non auth user create
    url = reverse("products-list")
    resp = api_client.post(url, payload)
    assert resp.status_code == HTTP_401_UNAUTHORIZED

    # non auth user update
    product = product_factory()
    url = reverse("products-detail", kwargs={'pk': product.id})
    resp = api_client.patch(url, payload)
    assert resp.status_code == HTTP_401_UNAUTHORIZED

    # non auth user delete
    product = product_factory()
    url = reverse("products-detail", kwargs={'pk': product.id})
    resp = api_client.delete(url, payload)
    assert resp.status_code == HTTP_401_UNAUTHORIZED

    # auth user create
    url = reverse("products-list")
    resp = api_auth_client.post(url, payload)
    assert resp.status_code == HTTP_403_FORBIDDEN

    # auth user update
    product = product_factory()
    url = reverse("products-detail", kwargs={'pk': product.id})
    resp = api_auth_client.patch(url, payload)
    assert resp.status_code == HTTP_403_FORBIDDEN

    # auth user delete
    product = product_factory()
    url = reverse("products-detail", kwargs={'pk': product.id})
    resp = api_auth_client.delete(url, payload)
    assert resp.status_code == HTTP_403_FORBIDDEN

    # admin create
    url = reverse("products-list")
    resp = api_auth_admin.post(url, payload)
    assert resp.status_code == HTTP_201_CREATED

    # admin update
    product = product_factory()
    url = reverse("products-detail", kwargs={'pk': product.id})
    resp = api_auth_admin.patch(url, payload)
    assert resp.status_code == HTTP_200_OK

    # admin delete
    product = product_factory()
    url = reverse("products-detail", kwargs={'pk': product.id})
    resp = api_auth_admin.delete(url, payload)
    assert resp.status_code == HTTP_204_NO_CONTENT


@pytest.mark.parametrize(
    ["price", "expected_status"],
    (
        ("400", HTTP_201_CREATED),
        ("-100", HTTP_400_BAD_REQUEST),
        ("100000000", HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_create_product(api_auth_admin, price, expected_status):

    # arrange
    payload = {
        'title': 'test',
        'price': price
    }
    url = reverse("products-list")

    # act
    resp = api_auth_admin.post(url, payload)

    # assert

    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json


@pytest.mark.django_db
def test_update_product(api_auth_admin, product_factory):
    # arrange

    product = product_factory()

    payload = {
        'title': 'test',
        'price': 500,
        'description': 'any text',
    }
    url = reverse("products-detail", kwargs={'pk': product.id})

    # act
    resp = api_auth_admin.patch(url, payload)

    # assert

    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 6  # fields count
    assert resp_json['id'] == product.id
    assert resp_json['title'] == payload['title']
    assert decimal.Decimal(resp_json['price']) == decimal.Decimal(payload['price'])
    assert resp_json['description'] == payload['description']


@pytest.mark.django_db
def test_delete_product(api_auth_admin, product_factory):

    # arrange
    product = product_factory()
    url = reverse("products-detail", kwargs={'pk': product.id})

    # act
    resp = api_auth_admin.delete(url)

    # assert
    assert resp.status_code == HTTP_204_NO_CONTENT

