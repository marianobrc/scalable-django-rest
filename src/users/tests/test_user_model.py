import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def test_password():
    return "test"


@pytest.mark.django_db
def test_user_create_minimal():
    User.objects.create_user(email="lennon@thebeatles.com", password="johnpassword")
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_superuser_create():
    User.objects.create_superuser(
        email="admin@thebeatles.com", password="adminpassword"
    )
    assert (
        User.objects.filter(is_staff=True, is_superuser=True, is_active=True).count()
        == 1
    )


@pytest.mark.django_db
def test_user_retrieve_by_email(create_user):
    user_email = "myemail@test.com"
    create_user(email=user_email)
    user = User.objects.get(email=user_email)
    assert user.email == user_email


@pytest.mark.django_db
def test_user_update_email(create_user):
    original_email = "myoriginalemail@test.com"
    new_email = "email@changed.com"
    create_user(email=original_email)
    user = User.objects.get(email=original_email)
    user.email = new_email
    user.save()
    user.refresh_from_db()
    assert user.email == new_email


@pytest.mark.django_db
def test_user_delete(create_user):
    user_email = "myemail@test.com"
    create_user(email=user_email)
    User.objects.filter(email=user_email).delete()
    assert not User.objects.filter(email=user_email).exists()
