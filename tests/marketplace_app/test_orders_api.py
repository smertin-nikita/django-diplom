import decimal

import pytest
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_201_CREATED


@pytest.mark.django_db
def test_retrieve_order_for_unauthorized_client(order_factory, api_client):
    # arrange
    order = order_factory()
    url = reverse("orders-detail", kwargs={'pk': order.id})

    # for UNAUTHORIZED client
    resp = api_client.get(url)
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_retrieve_order_for_not_owner_client(order_factory, api_client, user_factory):
    # arrange
    order = order_factory()
    url = reverse("orders-detail", kwargs={'pk': order.id})

    # for NOT OWNER client
    token = Token.objects.create(user=user_factory())
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    resp = api_client.get(url)
    assert resp.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_retrieve_order_for_admin_client(order_factory, api_client, user_factory):
    # arrange
    order = order_factory()
    url = reverse("orders-detail", kwargs={'pk': order.id})

    # for Admin client
    token = Token.objects.create(user=user_factory(is_staff=True))
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    resp = api_client.get(url)
    assert resp.status_code == HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_order_owner_client(order_factory, api_client, user_factory):
    # arrange
    order = order_factory()
    url = reverse("orders-detail", kwargs={'pk': order.id})

    # for OWNER client
    token = Token.objects.create(user=order.creator)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    resp = api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 7  # fields count
    assert resp_json['id'] == order.id
    assert resp_json['creator']['id'] == order.creator.id
    assert resp_json['status'] == order.status
    assert decimal.Decimal(resp_json['amount']) == order.amount
    for i, product in enumerate(resp_json['order_positions']):
        assert product


@pytest.mark.django_db
def test_list_orders_for_unauthorized_client(api_client, order_factory, user_factory):
    # arrange
    objs = order_factory(_quantity=10)
    url = reverse("orders-list")

    # for UNAUTHORIZED client
    resp = api_client.get(url)
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_orders_for_not_owner_client(api_client, order_factory, user_factory):
    # arrange
    objs = order_factory(_quantity=10)
    url = reverse("orders-list")

    # for NOT OWNER client
    token = Token.objects.create(user=user_factory())
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    resp = api_client.get(url)
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert len(resp_json) == 0


@pytest.mark.django_db
def test_list_orders_for_owner_client(api_client, order_factory):
    # arrange
    objs = order_factory(_quantity=10)
    url = reverse("orders-list")

    # for OWNER client
    token = Token.objects.create(user=objs[0].creator)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    resp = api_client.get(url)
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert len(resp_json) == 1


@pytest.mark.django_db
def test_list_orders_for_admin_client(api_client, order_factory, user_factory):
    # arrange
    objs = order_factory(_quantity=10)
    url = reverse("orders-list")

    # for Admin client
    token = Token.objects.create(user=user_factory(is_staff=True))
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    resp = api_client.get(url)
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert len(resp_json) == len(objs)


@pytest.mark.django_db
def test_create_order_for_unauthorized_client(api_client, order_positions_factory):
    # arrange
    payload = {
        'order_positions': order_positions_factory(_quantity=10)
    }
    url = reverse("orders-list")

    # for UNAUTHORIZED client
    resp = api_client.post(url, payload)
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_order_for_authorized_client(api_client, order_positions_factory, user_factory):
    # arrange
    payload = {
        'order_positions': order_positions_factory(_quantity=10)
    }
    url = reverse("orders-list")

    # for AUTH client
    token = Token.objects.create(user=user_factory())
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    resp = api_client.post(url, payload)
    assert resp.status_code == HTTP_201_CREATED


