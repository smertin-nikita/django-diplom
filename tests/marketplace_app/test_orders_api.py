import decimal

import pytest
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_201_CREATED, \
    HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_retrieve_order_for_unauthorized_client(order_factory, api_client):
    # arrange
    order = order_factory()
    url = reverse("orders-detail", kwargs={'pk': order.id})

    # for UNAUTHORIZED client
    resp = api_client.get(url)
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_retrieve_order_for_not_owner_client(order_factory, api_auth_client):
    # arrange
    order = order_factory()
    url = reverse("orders-detail", kwargs={'pk': order.id})

    # for NOT OWNER client
    resp = api_auth_client.get(url)
    assert resp.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_retrieve_order_for_admin_client(order_factory, api_auth_admin):
    # arrange
    order = order_factory()
    url = reverse("orders-detail", kwargs={'pk': order.id})

    # for Admin client
    resp = api_auth_admin.get(url)
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
    for i, product in enumerate(resp_json['positions']):
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
def test_list_orders_for_admin_client(api_auth_admin, order_factory, user_factory):
    # arrange
    objs = order_factory(_quantity=10)
    url = reverse("orders-list")

    # for Admin client
    resp = api_auth_admin.get(url)
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert len(resp_json) == len(objs)


@pytest.mark.django_db
def test_filter_status_orders(api_auth_admin, order_factory, user_factory):
    # arrange
    objs = order_factory(_quantity=10)
    test_obj_id = 0
    test_status = 'DONE'
    url = reverse("orders-detail", kwargs={'pk': objs[test_obj_id].id})
    resp = api_auth_admin.patch(url, {'status': 'DONE'})
    assert resp.status_code == HTTP_200_OK

    url = reverse("orders-list")

    # for Admin client
    resp = api_auth_admin.get(url, {'status': test_status})
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json[test_obj_id]['status'] == test_status


@pytest.mark.django_db
def test_order_filter_amount_orders(api_auth_admin, order_factory, user_factory):
    # arrange
    objs = order_factory(_quantity=10)
    max_amount = max(obj.amount for obj in objs)
    min_amount = min(obj.amount for obj in objs)

    url = reverse("orders-list")

    # for Admin client
    resp = api_auth_admin.get(url, {'ordering': 'amount'})
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert decimal.Decimal(resp_json[0]['amount']) == decimal.Decimal(min_amount)
    assert decimal.Decimal(resp_json[-1]['amount']) == decimal.Decimal(max_amount)


@pytest.mark.django_db
def test_filter_create_at_orders(api_auth_admin, order_factory):

    # arrange
    orders = order_factory(_quantity=10)
    url = reverse("orders-list")

    # act
    # Делаю slice с 2 по 7 включительно и того должно быть 6 записей
    resp = api_auth_admin.get(url, {'created_at_after': orders[2].created_at, 'created_at_before': orders[7].created_at})

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 6


@pytest.mark.django_db
def test_filter_updated_at_orders(api_auth_admin, order_factory):

    # arrange
    orders = order_factory(_quantity=10)
    url = reverse("orders-list")

    # act
    # Делаю slice с 2 по 7 включительно и того должно быть 6 записей
    resp = api_auth_admin.get(url, {'updated_at_after': orders[2].updated_at, 'updated_at_before': orders[7].updated_at})

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 6


@pytest.mark.django_db
def test_create_order_for_unauthorized_client(api_client, positions_factory):
    # arrange
    payload = {
        'positions': positions_factory(_quantity=10)
    }
    url = reverse("orders-list")

    # for UNAUTHORIZED client
    resp = api_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_order_for_authorized_client(api_client, positions_factory, user_factory, product_factory):
    # arrange
    products = product_factory(_quantity=10, price=100)
    # _quantity=10 * price=100
    test_amount = 10 * 100
    # quantity for order positions is 1
    payload = {
        "positions": positions_factory(products=products)
    }

    url = reverse("orders-list")

    # for AUTH client
    creator = user_factory()
    token = Token.objects.create(user=creator)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    resp = api_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_201_CREATED

    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 7  # fields count
    assert resp_json['creator']['id'] == creator.id
    assert decimal.Decimal(resp_json['amount']) == decimal.Decimal(test_amount)
    for i, obj in enumerate(resp_json['positions']):
        assert obj['product']['id'] == products[i].id


@pytest.mark.django_db
def test_validate_without_positions_on_create_order(api_auth_client, positions_factory, product_factory):
    # without order_positions
    payload = {}
    url = reverse("orders-list")
    # for AUTH client
    resp = api_auth_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_empty_positions_on_create_order(api_auth_client, positions_factory):
    # empty order_positions
    payload = {"positions": []}
    url = reverse("orders-list")
    resp = api_auth_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_miss_product_id_in_positions_on_create_order(api_auth_client, positions_factory):
    # empty order_positions
    payload = {"positions": [{}]}
    url = reverse("orders-list")
    resp = api_auth_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_not_exists_product_in_positions_on_create_order(
        api_auth_client, positions_factory, product_factory):

    product = product_factory()
    # NOT EXIST PRODUCT
    payload = {
        "positions": {'product_id': product.id + 1}
    }
    url = reverse("orders-list")
    # for AUTH client
    resp = api_auth_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_quantity_in_positions_on_create_order(api_auth_client, positions_factory, product_factory):
    # test quantity = 10001.00 cannot be more then 10000
    payload = {
        "positions": positions_factory(quantity=10001)
    }
    url = reverse("orders-list")
    # for AUTH client
    resp = api_auth_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_amount_on_create_order(api_auth_client, positions_factory, product_factory):
    # test amount = 10000000000.00 cannot be more then 100000000
    products = product_factory(_quantity=10, price=100000)
    payload = {
        "positions": positions_factory(products=products, quantity=10000)
    }
    url = reverse("orders-list")
    # for AUTH client
    resp = api_auth_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_status_for_not_admin_on_create_order(api_auth_client, positions_factory):
    # to Edit status allows only admins
    payload = {
        "positions": positions_factory(),
        "status": "DONE"
    }
    url = reverse("orders-list")
    # for AUTH client
    resp = api_auth_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    ["status", "expected_status_code"],
    (
        ("NEW", HTTP_201_CREATED),
        ("IN_PROGRESS", HTTP_201_CREATED),
        ("DONE", HTTP_201_CREATED),
        ("INVALID_STATUS", HTTP_400_BAD_REQUEST)
    )
)
@pytest.mark.django_db
def test_validate_status_on_create_order(status, expected_status_code, api_auth_admin, positions_factory):
    payload = {
        "positions": positions_factory(),
        "status": status
    }
    url = reverse("orders-list")
    # for AUTH client
    resp = api_auth_admin.post(url, payload, format='json')
    assert resp.status_code == expected_status_code


@pytest.mark.django_db
def test_update_order_for_unauthorized_client(api_client, positions_factory, order_factory):
    # arrange
    order = order_factory()
    payload = {
        'positions': positions_factory(_quantity=10)
    }
    url = reverse("orders-detail", kwargs={'pk': order.id})

    # for UNAUTHORIZED client
    resp = api_client.patch(url, payload, format='json')
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_update_order_for_owner_client(api_client, positions_factory, order_factory, user_factory):
    # arrange
    creator = user_factory()
    token = Token.objects.create(user=creator)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    payload = {
        'positions': positions_factory(_quantity=10)
    }

    # for OWNER client
    # create
    url = reverse("orders-list")
    resp = api_client.post(url, payload, format='json')
    resp_json = resp.json()
    assert resp.status_code == HTTP_201_CREATED

    # update
    url = reverse("orders-detail", kwargs={'pk': resp_json['id']})
    resp = api_client.patch(url, payload, format='json')
    assert resp.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_order_for_admin_client(api_auth_admin, positions_factory, order_factory, user_factory, api_client):
    # arrange
    creator = user_factory()
    token = Token.objects.create(user=creator)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    payload = {
        'positions': positions_factory(_quantity=10)
    }

    # for OWNER client
    # create
    url = reverse("orders-list")
    resp = api_client.post(url, payload, format='json')
    order = resp.json()
    assert resp.status_code == HTTP_201_CREATED

    # update
    payload = {
        'positions': positions_factory(_quantity=10),
        'amount': decimal.Decimal(1),
        'status': 'DONE'
    }
    # for ADMIN client
    url = reverse("orders-detail", kwargs={'pk': order['id']})
    resp = api_auth_admin.patch(url, payload, format='json')
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 7  # fields count
    assert resp_json['creator']['id'] == order['creator']['id']
    assert resp_json['amount'] == order['amount']
    assert resp_json['status'] == payload['status']
    for i, obj in enumerate(resp_json['positions']):
        assert obj['product']['id'] == order['positions'][i]['product']['id']



