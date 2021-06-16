import pytest
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, \
    HTTP_201_CREATED, HTTP_204_NO_CONTENT


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
    for i, item in enumerate(resp_json['products']):
        assert item['product']['id']


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
    resp = api_auth_admin.post(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_validate_miss_products_on_create_collection(api_auth_admin, collection_factory):
    # arrange
    payload = {
        'title': 'test'
    }
    url = reverse("product-collections-list")
    # for admin user
    resp = api_auth_admin.post(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_validate_empty_products_on_create_collection(api_auth_admin, collection_factory):
    # arrange
    payload = {
        'title': 'test',
        "products": []
    }
    url = reverse("product-collections-list")
    # for admin user
    resp = api_auth_admin.post(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_validate_miss_product_id_products_on_create_collection(api_auth_admin, collection_factory):
    # arrange
    payload = {
        'title': 'test',
        'products': [{}]
    }
    url = reverse("product-collections-list")
    # for admin user
    resp = api_auth_admin.post(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_create_collection_for_unauthorized_client(api_client):
    # arrange
    url = reverse("product-collections-list")

    # for non auth user
    resp = api_client.post(url)
    assert resp.status_code == HTTP_401_UNAUTHORIZED
    print(resp.rendered_content)


@pytest.mark.django_db
def test_create_collection_for_nonadmin_client(api_auth_client, collection_factory):
    # arrange
    url = reverse("product-collections-list")

    # for non admin user
    resp = api_auth_client.post(url)
    assert resp.status_code == HTTP_403_FORBIDDEN
    print(resp.rendered_content)


@pytest.mark.django_db
def test_validate_product_that_does_not_exist_on_create_collection(api_auth_admin):

    # arrange
    payload = {
        'title': 'test',
        'products': [{'product_id': 1}]  # product's id that does not exist
    }
    url = reverse("product-collections-list")

    # for auth user
    resp = api_auth_admin.post(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_create_collection_for_admin_client(api_auth_admin, product_ids_factory):
    # arrange
    payload = {
        "title": 'test',
        "products": product_ids_factory(_quantity=10)
    }
    url = reverse("product-collections-list")

    # for admin user
    resp = api_auth_admin.post(url, payload, format='json')
    assert resp.status_code == HTTP_201_CREATED
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 6  # fields count
    assert resp_json['title'] == payload['title']
    for i, item in enumerate(resp_json['products']):
        assert item['product']['id'] == payload['products'][i]['product_id']


@pytest.mark.django_db
def test_update_collection_for_unauthorized_client(api_client, collection_factory):
    # arrange
    collection = collection_factory()
    url = reverse("product-collections-detail", kwargs={'pk': collection.id})

    # for non auth user
    resp = api_client.patch(url)
    assert resp.status_code == HTTP_401_UNAUTHORIZED
    print(resp.rendered_content)


@pytest.mark.django_db
def test_update_collection_for_nonadmin_client(api_auth_client, collection_factory):
    # arrange
    collection = collection_factory()
    url = reverse("product-collections-detail", kwargs={'pk': collection.id})

    # for non admin user
    resp = api_auth_client.patch(url)
    assert resp.status_code == HTTP_403_FORBIDDEN
    print(resp.rendered_content)


@pytest.mark.django_db
def test_validate_empty_products_on_update_collection(api_auth_admin, collection_factory):
    # arrange
    collection = collection_factory()
    payload = {
        'products': []
    }
    url = reverse("product-collections-detail", kwargs={'pk': collection.id})

    # for admin user
    resp = api_auth_admin.patch(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_validate_miss_product_id_products_on_update_collection(api_auth_admin, collection_factory):
    # arrange
    collection = collection_factory()
    payload = {
        'products': [{}]
    }
    url = reverse("product-collections-detail", kwargs={'pk': collection.id})

    # for admin user
    resp = api_auth_admin.patch(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_validate_product_that_does_not_exist_on_update_collection(api_auth_admin, collection_factory):

    # arrange
    collection = collection_factory()
    payload = {
        'products': [{'product_id': 22}]  # product's id that does not exist
    }
    url = reverse("product-collections-detail", kwargs={'pk': collection.id})

    # for auth user
    resp = api_auth_admin.patch(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_update_collection_for_admin_client(api_auth_admin, collection_factory, product_ids_factory):

    # arrange
    collection = collection_factory()
    payload = {
        'title': 'test',
        'text': 'test text',
        'products':  product_ids_factory(_quantity=10)
    }
    url = reverse("product-collections-detail", kwargs={'pk': collection.id})

    # for auth user
    resp = api_auth_admin.patch(url, payload, format='json')
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert len(resp_json) == 6  # fields count
    assert resp_json['id'] == collection.id
    assert resp_json['title'] == payload['title']
    assert resp_json['text'] == payload['text']
    for i, item in enumerate(resp_json['products']):
        assert item['product']['id'] == payload['products'][i]['product_id']


@pytest.mark.django_db
def test_delete_collection_for_admin_client(api_client, collection_factory):
    # arrange
    collection = collection_factory()

    # for unauthorized
    url = reverse("product-collections-detail", kwargs={'pk': collection.id})
    resp = api_client.delete(url)
    assert resp.status_code == HTTP_401_UNAUTHORIZED
    print(resp.rendered_content)


@pytest.mark.django_db
def test_delete_collection_for_non_admin_client(api_auth_client, collection_factory):
    # arrange
    collection = collection_factory()

    # for non-admin
    url = reverse("product-collections-detail", kwargs={'pk': collection.id})
    resp = api_auth_client.delete(url)
    assert resp.status_code == HTTP_403_FORBIDDEN
    print(resp.rendered_content)


@pytest.mark.django_db
def test_delete_collection_for_admin_client(api_auth_admin, collection_factory):
    # arrange
    collection = collection_factory()

    # for admin
    url = reverse("product-collections-detail", kwargs={'pk': collection.id})
    resp = api_auth_admin.delete(url)
    assert resp.status_code == HTTP_204_NO_CONTENT


