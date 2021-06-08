import pytest
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_review(api_client, review_factory):

    # arrange
    obj = review_factory()

    url = reverse("product-reviews-detail", kwargs={'pk': obj.id})

    # act
    resp = api_client.get(url)

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 7  # fields count
    assert resp_json['id'] == obj.id
    assert resp_json['creator']['id'] == obj.creator.id
    assert resp_json['product']['id'] == obj.product.id
    assert resp_json['text'] == obj.text
    assert resp_json['mark'] == obj.mark


@pytest.mark.django_db
def test_list_products(api_client, review_factory):

    # arrange
    objs = review_factory(_quantity=10)

    url = reverse("product-reviews-list")

    # act
    resp = api_client.get(url)

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == len(objs)
    for i, obj in enumerate(resp_json):
        assert obj['id'] == objs[i].id
        assert obj['creator']['id'] == objs[i].creator.id
        assert obj['product']['id'] == objs[i].product.id
        assert obj['text'] == objs[i].text
        assert obj['mark'] == objs[i].mark


@pytest.mark.django_db
def test_create_products(api_client, review_factory):

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
