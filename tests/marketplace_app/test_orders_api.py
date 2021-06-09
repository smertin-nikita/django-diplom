import pytest
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_retrieve_order_with_permissions(api_client, api_auth_client, api_auth_admin, api_auth_another_client, order_factory):

    # arrange
    obj = order_factory()
    url = reverse("orders-detail", kwargs={'pk': obj.id})

    # todo Придумать как вытаскивать клиента из obj

    # for UNAUTHORIZED client
    resp = api_client.get(url)
    assert resp.status_code == HTTP_401_UNAUTHORIZED

    # for not owner client
    resp = api_client.get(url)
    assert resp.status_code == HTTP_401_UNAUTHORIZED

    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 8  # fields count
    assert resp_json['id'] == obj.id
    assert resp_json['creator']['id'] == obj.creator.id
    assert resp_json['product']['id'] == obj.product.id
    assert resp_json['product_id'] == obj.product_id
    assert resp_json['text'] == obj.text
    assert resp_json['mark'] == obj.mark