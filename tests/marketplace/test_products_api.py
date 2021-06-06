import pytest
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_product(api_client, product_factory):

    # arrange
    product = product_factory()

    url = reverse("product-detail", kwargs={'pk': product.id})

    # act
    resp = api_client.get(url)

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 3  # fields count
    assert resp_json['id'] == product.id
    assert resp_json['title'] == product.title
