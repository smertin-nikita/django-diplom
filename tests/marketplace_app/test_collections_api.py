import pytest
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST


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


@pytest.mark.django_db
def test_list_collection(api_client, collection_factory):
    # arrange
    objs = collection_factory(_quantity=10)
    url = reverse("product-collections-list")

    # act
    resp = api_client.get(url)

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == len(objs)
    for i, item in enumerate(resp_json):
        assert item['id'] == objs[i].id
        assert item['title'] == objs[i].title
        assert item['text'] == objs[i].text


@pytest.mark.django_db
def test_validate_miss_title_on_create_collection(api_auth_admin, collection_factory, product_ids_factory):
    # arrange
    payload = {
        'products': product_ids_factory(_quantity=10)
    }
    url = reverse("product-collections-list")
    # for admin user
    resp = api_auth_admin.post(url, payload)
    assert resp.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_miss_products_on_create_collection(api_auth_admin, collection_factory):
    # arrange
    payload = {
        'title': 'test'
    }
    url = reverse("product-collections-list")
    # for admin user
    resp = api_auth_admin.post(url, payload)
    assert resp.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_empty_products_on_create_collection(api_auth_admin, collection_factory):
    # arrange
    payload = {
        'title': 'test',
        'products': []
    }
    url = reverse("product-collections-list")
    # for admin user
    resp = api_auth_admin.post(url, payload)
    assert resp.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_miss_product_id_products_on_create_collection(api_auth_admin, collection_factory):
    # arrange
    payload = {
        'title': 'test',
        'products': [{}]
    }
    url = reverse("product-collections-list")
    # for admin user
    resp = api_auth_admin.post(url, payload)
    assert resp.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_collection_for_unauthorized_client(api_client, collection_factory):
    # arrange
    url = reverse("product-collections-list")

    # for non auth user
    resp = api_client.post(url)
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_collection_for_nonadmin_client(api_auth_client, collection_factory):
    # arrange
    url = reverse("product-collections-list")
    payload = {
        'title': ''
    }
    # for non auth user
    resp = api_auth_client.post(url)
    assert resp.status_code == HTTP_401_UNAUTHORIZED