import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_user_retrieve(create_user, api_client):
    # Create a user
    test_email = "user@test.com"
    test_password = "MyPassw0Rd123"
    user = create_user(email=test_email, password=test_password)
    # Authenticate teh user
    api_client.force_authenticate(user)
    # Retrieve user details
    user_details_url = reverse("rest_user_details")
    response = api_client.get(user_details_url, format="json")
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "pk" in response_data
    assert "email" in response_data
    assert "first_name" in response_data
    assert "last_name" in response_data
    assert response_data["pk"]
    assert response_data["email"] == test_email
