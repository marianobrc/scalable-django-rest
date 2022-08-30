import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_password():
    return "test"


@pytest.fixture
def create_user(db, django_user_model, test_password):
    def make_user(**kwargs):
        if "password" not in kwargs:
            kwargs["password"] = test_password
        if "email" not in kwargs:
            kwargs["email"] = "user@test.com"
        return django_user_model.objects.create_user(**kwargs)

    return make_user
