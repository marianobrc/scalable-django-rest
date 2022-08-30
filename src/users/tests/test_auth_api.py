import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_login(create_user, api_client):
    test_email = "user@test.com"
    test_password = "MyPassw0Rd123"
    create_user(email=test_email, password=test_password)
    login_data = {
        "username": test_email,
        "password": test_password,
    }
    login_url = reverse("rest_login")
    response = api_client.post(login_url, data=login_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["access_token"]  # Not None, Not Empty
    assert response_data["refresh_token"]  # Not None, Not Empty
    assert response_data["user"]  # Not None, Not Empty
    assert response_data["user"]["pk"]  # Not None, Not Empty
    assert response_data["user"]["email"] == test_email
