import pytest
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_retrieve_order_with_permissions(order_factory, api_client, user_factory):

    # arrange
    order = order_factory()
    url = reverse("orders-detail", kwargs={'pk': order.id})

    # for UNAUTHORIZED client
    resp = api_client.get(url)
    assert resp.status_code == HTTP_401_UNAUTHORIZED

    # for NOT OWNER client
    token = Token.objects.create(user=user_factory())
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    resp = api_client.get(url)
    assert resp.status_code == HTTP_404_NOT_FOUND

    # for OWNER client
    token = Token.objects.create(user=order.creator)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    resp = api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    # todo попробовать остальные поля
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 7  # fields count
    assert resp_json['id'] == order.id
    assert resp_json['creator']['id'] == order.creator.id
    # assert resp_json['product_id'] == order.product_id
    assert resp_json['status'] == order.status
