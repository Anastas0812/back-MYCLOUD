import pytest
from rest_framework.test import APIClient
from users.models import User


@pytest.mark.django_db
def test_get_users_as_admin():
    client = APIClient()

    admin = User.objects.create_user(
        username='admin_test',
        password='Admin123!',
        is_admin=True
    )

    client.login(username='admin_test', password='Admin123!')

    response = client.get('/api/users/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_users_not_admin():
    client = APIClient()

    user = User.objects.create_user(
        username='user_test',
        password='User123!',
        is_admin=False
    )

    client.login(username='user_test', password='User123!')

    response = client.get('/api/users/')
    assert response.status_code == 403


@pytest.mark.django_db
def test_register():
    client = APIClient()

    response = client.post('/api/users/register/', {
        'username': 'haker2000',
        'full_name': 'Тестовый Юзер',
        'email': 'new@mail.ru',
        'password': 'Parol12345!'
    })
    assert response.status_code == 201

@pytest.mark.django_db
def test_login():
    client = APIClient()

    user = User.objects.create_user(
        username='Alla',
        password='Parol12345!',
        is_admin=False
    )

    response = client.post('/api/users/login/', {
        'username': 'Alla',
        'password': 'Parol12345!'
    })
    assert response.status_code == 200