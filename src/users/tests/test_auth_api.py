from datetime import datetime
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_login(create_user, api_client):
    test_email = "user@test.com"
    test_password = "MyPassw0Rd123"
    create_user(email=test_email, password=test_password)
    login_data = {
        "email": test_email,
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


@pytest.mark.django_db
def test_logout(create_user, api_client):
    test_email = "user@test.com"
    test_password = "MyPassw0Rd123"
    create_user(email=test_email, password=test_password)
    login_data = {
        "email": test_email,
        "password": test_password,
    }
    login_url = reverse("rest_login")
    response = api_client.post(login_url, data=login_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    logout_url = reverse("rest_logout")
    response = api_client.post(logout_url, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_jwt_verification_with_valid_token(create_user, api_client):
    test_email = "user@test.com"
    test_password = "MyPassw0Rd123"
    create_user(email=test_email, password=test_password)
    # Login to get a valid token
    login_data = {
        "email": test_email,
        "password": test_password,
    }
    login_url = reverse("rest_login")
    response = api_client.post(login_url, data=login_data, format="json")
    response_data = response.json()
    access_token = response_data["access_token"]
    assert response.status_code == status.HTTP_200_OK
    # Call the verification endpoint with a valid token
    token_verification_url = reverse("token_verify")
    response = api_client.post(
        token_verification_url, data={"token": access_token}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_jwt_verification_with_wrong_token(create_user, api_client):
    access_token = "not.a.token"
    # Call the verification endpoint with a valid token
    token_verification_url = reverse("token_verify")
    response = api_client.post(
        token_verification_url, data={"token": access_token}, format="json"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_jwt_refresh(create_user, api_client):
    test_email = "user@test.com"
    test_password = "MyPassw0Rd123"
    create_user(email=test_email, password=test_password)
    # Login to get a valid token
    login_data = {
        "email": test_email,
        "password": test_password,
    }
    login_url = reverse("rest_login")
    response = api_client.post(login_url, data=login_data, format="json")
    login_response_data = response.json()
    refresh_token = login_response_data["refresh_token"]
    assert response.status_code == status.HTTP_200_OK
    # Call the refresh endpoint with a valid token
    token_verification_url = reverse("token_refresh")
    current_time = datetime.utcnow()
    response = api_client.post(
        token_verification_url, data={"refresh": refresh_token}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    # Check that we got a new access token
    refresh_response_data = response.json()
    assert "access" in refresh_response_data
    assert refresh_response_data["access"] != login_response_data["access_token"]
    assert "access_token_expiration" in refresh_response_data
    # Check is the expiration date is in the future
    expiration_time = datetime.strptime(
        refresh_response_data["access_token_expiration"], "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    assert expiration_time > current_time
