import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Фикстура для клиента API"""
    return APIClient()


@pytest.fixture
def product_factory():
    def func(**kwargs):
        return baker.make('product', **kwargs)

    return func


@pytest.fixture
def user_factory():
    def func(**kwargs):
        return baker.make(get_user_model(), **kwargs)

    return func
