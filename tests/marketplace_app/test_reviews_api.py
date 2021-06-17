import pytest
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, HTTP_400_BAD_REQUEST,\
    HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN


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
        assert obj['text'] == objs[i].text
        assert obj['mark'] == objs[i].mark


@pytest.mark.django_db
def test_filter_creator_id_for_reviews(api_client, review_factory):

    # arrange
    reviews = review_factory(_quantity=10)
    url = reverse("product-reviews-list")

    # act
    # Ищем по первому отзыву. Creator в каждом review уникальный
    resp = api_client.get(url, {'creator': reviews[0].creator.id})

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 1
    assert resp_json[0]['id'] == reviews[0].id
    assert resp_json[0]['creator']['id'] == reviews[0].creator.id
    assert resp_json[0]['product']['id'] == reviews[0].product.id
    assert resp_json[0]['text'] == reviews[0].text
    assert resp_json[0]['mark'] == reviews[0].mark


@pytest.mark.django_db
def test_filter_product_id_for_reviews(api_client, review_factory):

    # arrange
    reviews = review_factory(_quantity=10)
    url = reverse("product-reviews-list")

    # act
    # Ищем по первому отзыву. Product в каждом review уникальный
    resp = api_client.get(url, {'product': reviews[0].product.id})

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 1
    assert resp_json[0]['id'] == reviews[0].id
    assert resp_json[0]['creator']['id'] == reviews[0].creator.id
    assert resp_json[0]['product']['id'] == reviews[0].product.id
    assert resp_json[0]['text'] == reviews[0].text
    assert resp_json[0]['mark'] == reviews[0].mark


@pytest.mark.django_db
def test_filter_create_at_reviews(api_client, review_factory):

    # arrange
    reviews = review_factory(_quantity=10)
    url = reverse("product-reviews-list")

    # act
    resp = api_client.get(url, {'created_at_after': reviews[0].created_at, 'created_at_before': reviews[0].created_at})

    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 1


@pytest.mark.django_db
def test_create_reviews_for_unauthorized_client(api_client, product_factory):

    product = product_factory()
    # arrange
    payload = {
        'mark': 3,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # for non auth user
    resp = api_client.post(url, payload)
    assert resp.status_code == HTTP_401_UNAUTHORIZED
    print(resp.rendered_content)


@pytest.mark.django_db
def test_create_reviews_for_authorized_client(api_auth_client, product_factory):
    product = product_factory()
    # arrange
    payload = {
        'mark': 3,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # for auth user
    resp = api_auth_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_201_CREATED
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 7  # fields count
    assert resp_json['product']['id'] == payload['product_id']
    assert resp_json['mark'] == payload['mark']


@pytest.mark.django_db
def test_validate_miss_mark_on_create_review(api_auth_client, product_factory):

    product = product_factory()
    # arrange
    payload = {
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # act for auth user
    resp = api_auth_client.post(url, payload, format='json')
    # assert for auth user
    assert resp.status_code == HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.parametrize(
    ["mark", "expected_status"],
    (
        ("3", HTTP_201_CREATED),
        ("6", HTTP_400_BAD_REQUEST),
        ("0", HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_validate_mark_on_create_review(api_auth_client, product_factory, mark, expected_status):

    product = product_factory()
    # arrange
    payload = {
        'mark': mark,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # act for auth user
    resp = api_auth_client.post(url, payload, format='json')
    # assert for auth user
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json


@pytest.mark.django_db
def test_validate_miss_product_on_create_review(api_auth_client, product_factory):

    # arrange
    payload = {
        'mark': 3,
    }
    url = reverse("product-reviews-list")

    # for auth user
    resp = api_auth_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_validate_product_that_does_not_exist_on_create_review(api_auth_client):

    # arrange
    payload = {
        'mark': 3,
        'product_id': 1  # product's id that does not exist
    }
    url = reverse("product-reviews-list")

    # for auth user
    resp = api_auth_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_validate_product_that_exist_on_create_review(api_auth_client, product_factory):
    # arrange
    url = reverse("product-reviews-list")
    product = product_factory()
    payload = {
        'mark': 3,
        'product_id': product.id  # product's id that exists
    }

    # for auth user
    resp = api_auth_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_201_CREATED


@pytest.mark.django_db
def test_validate_product_with_unique_together_with_creator_on_create_review(api_auth_client, product_factory):
    # arrange
    url = reverse("product-reviews-list")
    product = product_factory()
    payload = {
        'mark': 3,
        'product_id': product.id  # product's id that exists
    }
    # for auth user
    resp = api_auth_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_201_CREATED

    # Unique together user and product
    # for auth user
    resp = api_auth_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_update_review_for_unauthorized_client(api_client, product_factory, review_factory):
    # arrange
    review = review_factory()
    product = product_factory()
    payload = {
        'mark': 3,
        'product_id': product.id
    }
    url = reverse("product-reviews-detail", kwargs={'pk': review.id})
    # for UNAUTHORIZED client
    resp = api_client.patch(url, payload, format='json')
    assert resp.status_code == HTTP_401_UNAUTHORIZED
    print(resp.rendered_content)


@pytest.mark.django_db
def test_update_review_for_non_owner_client(api_auth_client, product_factory, api_auth_another_client):
    # arrange
    product = product_factory()
    payload = {
        'mark': 3,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # Create review
    # act for auth user
    resp = api_auth_client.post(url, payload, format='json')
    resp_json = resp.json()
    review_id = resp_json['id']

    url = reverse("product-reviews-detail", kwargs={'pk': review_id})

    # updated payload
    payload = {
        'mark': 3
    }

    # only owners can update
    # for not owners
    resp = api_auth_another_client.patch(url, payload, format='json')
    assert resp.status_code == HTTP_403_FORBIDDEN
    print(resp.rendered_content)


@pytest.mark.django_db
def test_update_review_for_admin_client(api_auth_client, product_factory, api_auth_admin):
    # arrange
    product = product_factory()
    payload = {
        'mark': 3,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # Create review
    # act for auth user
    resp = api_auth_client.post(url, payload, format='json')
    resp_json = resp.json()
    review_id = resp_json['id']

    url = reverse("product-reviews-detail", kwargs={'pk': review_id})

    # updated payload
    payload = {
        'mark': 3
    }

    # for admin
    resp = api_auth_admin.patch(url, payload, format='json')
    assert resp.status_code == HTTP_403_FORBIDDEN
    print(resp.rendered_content)


@pytest.mark.django_db
def test_update_review_for_owner_client(api_auth_client, product_factory):
    # arrange
    product = product_factory()
    payload = {
        'mark': 3,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # Create review
    # act for auth user
    resp = api_auth_client.post(url, payload, format='json')
    resp_json = resp.json()
    review_id = resp_json['id']

    url = reverse("product-reviews-detail", kwargs={'pk': review_id})

    # updated payload
    payload = {
        'mark': 3
    }

    # for owner
    resp = api_auth_client.patch(url, payload, format='json')
    assert resp.status_code == HTTP_200_OK


@pytest.mark.django_db
def test_validate_same_product_on_update_review(api_auth_client, product_factory):
    # arrange
    product = product_factory()
    payload = {
        'mark': 3,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # Create review
    # act for auth user
    resp = api_auth_client.post(url, payload, format='json')
    resp_json = resp.json()
    review_id = resp_json['id']

    # change payload for update with the same product
    payload = {
        'product_id': product.id
    }
    url = reverse("product-reviews-detail", kwargs={'pk': review_id})
    # act
    resp = api_auth_client.patch(url, payload, format='json')
    # assert
    assert resp.status_code == HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_validate_product_that_does_not_exist_on_update_review(api_auth_client, product_factory):
    # arrange
    product = product_factory()
    payload = {
        'mark': 3,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # Create review
    # act for auth user
    resp = api_auth_client.post(url, payload, format='json')
    resp_json = resp.json()
    review_id = resp_json['id']

    # change payload for update with does not exist product
    payload = {
        'product_id': product.id + 1
    }
    url = reverse("product-reviews-detail", kwargs={'pk': review_id})
    resp = api_auth_client.patch(url, payload, format='json')
    assert resp.status_code == HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_validate_new_product_on_update_review(api_auth_client, product_factory):
    # arrange
    product = product_factory()
    payload = {
        'mark': 3,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # Create review
    # act for auth user
    resp = api_auth_client.post(url, payload, format='json')
    resp_json = resp.json()
    review_id = resp_json['id']

    # change payload for update with new product
    product = product_factory()
    payload = {
        'product_id': product.id
    }
    url = reverse("product-reviews-detail", kwargs={'pk': review_id})
    # act
    resp = api_auth_client.patch(url, payload, format='json')
    # assert
    assert resp.status_code == HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 7  # fields count
    assert resp_json['id'] == review_id
    assert resp_json['product']['id'] == payload['product_id']


@pytest.mark.parametrize(
    ["mark", "expected_status"],
    (
        ("3", HTTP_200_OK),
        ("6", HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_validate_mark_on_update_review(api_auth_client, mark, expected_status, product_factory):

    # arrange
    product = product_factory()
    payload = {
        'mark': 3,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # Create review
    # act for auth user
    resp = api_auth_client.post(url, payload, format='json')
    resp_json = resp.json()
    review_id = resp_json['id']

    # Change payload for update
    payload = {
        'mark': mark,
    }
    url = reverse("product-reviews-detail", kwargs={'pk': review_id})

    # for auth user
    resp = api_auth_client.patch(url, payload, format='json')
    assert resp.status_code == expected_status


@pytest.mark.django_db
def test_delete_review_for_unauthorized_client(api_client, api_auth_client, review_factory):
    # arrange
    review = review_factory()

    # UNAUTHORIZED
    url = reverse("product-reviews-detail", kwargs={'pk': review.id})
    resp = api_client.delete(url)
    assert resp.status_code == HTTP_401_UNAUTHORIZED
    print(resp.rendered_content)


@pytest.mark.django_db
def test_delete_product_for_not_owner(api_auth_client, product_factory, api_auth_another_client):
    # arrange
    product = product_factory()
    payload = {
        'mark': 3,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # Create review
    # act for auth user
    resp = api_auth_client.post(url, payload, format='json')
    resp_json = resp.json()
    review_id = resp_json['id']

    # for not owner
    url = reverse("product-reviews-detail", kwargs={'pk': review_id})
    resp = api_auth_another_client.delete(url)
    assert resp.status_code == HTTP_403_FORBIDDEN
    print(resp.rendered_content)


@pytest.mark.django_db
def test_delete_review_for_owner(api_auth_client, product_factory):
    # arrange
    product = product_factory()
    payload = {
        'mark': 3,
        'product_id': product.id
    }
    url = reverse("product-reviews-list")

    # Create review
    # act for auth user
    resp = api_auth_client.post(url, payload, format='json')
    resp_json = resp.json()
    review_id = resp_json['id']
    # for owner
    url = reverse("product-reviews-detail", kwargs={'pk': review_id})
    resp = api_auth_client.delete(url)
    assert resp.status_code == HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_review_for_admin(api_auth_admin, review_factory):
    # for admin
    review = review_factory()
    url = reverse("product-reviews-detail", kwargs={'pk': review.id})
    resp = api_auth_admin.delete(url)
    assert resp.status_code == HTTP_204_NO_CONTENT

