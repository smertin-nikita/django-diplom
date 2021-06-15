import pytest
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_collection(api_client, collection_factory):
    # arrange
    obj = collection_factory()
    url = reverse("product-collections-detail", kwargs={'pk': obj.id})

    # act
    resp = api_client.get(url)

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 6  # fields count
    assert resp_json['id'] == obj.id
    assert resp_json['title'] == obj.title
    assert resp_json['text'] == obj.text
    for i, product in enumerate(resp_json['products']):
        assert product['id'] == obj.products[i].id
