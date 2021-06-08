import pytest
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, \
    HTTP_405_METHOD_NOT_ALLOWED, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN


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
    assert len(resp_json) == 8  # fields count
    assert resp_json['id'] == obj.id
    assert resp_json['creator']['id'] == obj.creator.id
    assert resp_json['product']['id'] == obj.product.id
    assert resp_json['product_id'] == obj.product_id
    assert resp_json['text'] == obj.text
    assert resp_json['mark'] == obj.mark


@pytest.mark.django_db
def test_list_reviews(api_client, review_factory):

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
        assert obj['product_id'] == objs[i].product_id
        assert obj['text'] == objs[i].text
        assert obj['mark'] == objs[i].mark


@pytest.mark.django_db
def test_create_reviews(api_client, api_auth_client, api_auth_admin, review_factory, product_factory):

    product = product_factory()
    # arrange
    payload = {
        'mark': 3,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # act for non auth user
    resp = api_client.post(url, payload)
    # assert for non auth user
    assert resp.status_code == HTTP_401_UNAUTHORIZED

    # act for auth user
    resp = api_auth_client.post(url, payload)
    # assert for auth user
    assert resp.status_code == HTTP_201_CREATED
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 8  # fields count
    assert resp_json['product']['id'] == payload['product_id']
    assert resp_json['product_id'] == payload['product_id']
    assert resp_json['mark'] == payload['mark']

    # act for admin
    resp = api_auth_admin.post(url, payload)
    # assert for admin
    assert resp.status_code == HTTP_201_CREATED


@pytest.mark.parametrize(
    ["mark", "expected_status"],
    (
        ("3", HTTP_201_CREATED),
        ("6", HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_validate_mark(api_auth_client, review_factory, product_factory, mark, expected_status):

    product = product_factory()
    # arrange
    payload = {
        'mark': mark,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # act for auth user
    resp = api_auth_client.post(url, payload)
    # assert for auth user
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json


@pytest.mark.django_db
def test_validate_product(api_auth_client, review_factory, product_factory):

    # arrange
    payload = {
        'mark': 3,
        'product_id': 1  # product's id that does not exist
    }
    url = reverse("product-reviews-list")

    # act for auth user
    resp = api_auth_client.post(url, payload)
    # assert for auth user
    assert resp.status_code == HTTP_400_BAD_REQUEST

    product = product_factory()
    payload = {
        'mark': 3,
        'product_id': product.id  # product's id that exists
    }
    # act for auth user
    resp = api_auth_client.post(url, payload)
    # assert for auth user
    assert resp.status_code == HTTP_201_CREATED

    # Unique together user and product
    # act for auth user
    resp = api_auth_client.post(url, payload)
    # assert for auth user
    assert resp.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_review(api_auth_client, product_factory, review_factory):
    # arrange
    product = product_factory()
    # arrange
    payload = {
        'mark': 3,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # only owners can update
    # act
    resp = api_auth_client.patch(url, payload)
    # assert
    assert resp.status_code == HTTP_403_FORBIDDEN

    # act for auth user
    resp = api_auth_client.post(url, payload)
    # assert for auth user
    assert resp.status_code == HTTP_201_CREATED
    resp_json = resp.json()
    assert resp_json
    assert resp_json['id']

    payload = {
        'mark': 3,
        'text': 'any text'
    }
    url = reverse("product-reviews-detail", kwargs={'pk': resp_json['id']})

    # act
    resp = api_auth_client.patch(url, payload)

    # assert

    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 8  # fields count
    assert resp_json['id'] == resp_json['id']
    assert resp_json['mark'] == payload['mark']
    assert resp_json['text'] == payload['text']


@pytest.mark.django_db
def test_delete_product(api_auth_admin, review_factory):

    # arrange
    review = review_factory()
    url = reverse("product-reviews-detail", kwargs={'pk': review.id})

    # act
    resp = api_auth_admin.delete(url)

    # assert
    assert resp.status_code == HTTP_204_NO_CONTENT

    # arrange
    review = review_factory()
    url = reverse("product-reviews-detail", kwargs={'pk': review.id})

    # act
    resp = api_auth_admin.delete(url)

    # assert
    assert resp.status_code == HTTP_204_NO_CONTENT

