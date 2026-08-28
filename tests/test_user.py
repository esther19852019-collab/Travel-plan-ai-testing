import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.schemas.user import UserCreate
from app.main import app, users
client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_users():
    users.clear()

def test_create_user_valid_email_and_password():
    user = UserCreate(
        email="test@example.com",
        password="password123",
    )
    assert user.email == "test@example.com"
    assert user.password == "password123"

def test_create_user_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            email="not-an-email",
            password="password123",
        )


def test_create_user_short_password():
    with pytest.raises(ValidationError):
        UserCreate(
            email="test@example.com",
            password="123",
        )
# test if the user registration endpoint works correctly
def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201
    data = response.json()

    assert data["email"] == "newuser@example.com"


#test the duplicate email registration endpoint
def test_register_duplicate_email():
    user_data = {
        "email": "duplicate@example.com",
        "password": "password123",
    }

    first_response = client.post(
        "/auth/register",
        json=user_data
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/register",
        json = user_data,
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"]== "Email already registered"
    
# test the user registration endpoint with invalid input
@pytest.mark.parametrize(
    "user_data",
    [
        {
            "email": "invalid-email",
            "password": "password123",
        }
    ]
)

def test_register_user_invalid_input(user_data):
    response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert response.status_code == 422

def test_login_user():
    response = client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_wrong_password():
    client.post(
        "/auth/register",
        json={
            "email": "wrongpassword@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrongpassword@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401

def test_login_user_not_found():
    response = client.post(
        "/auth/login",
        json={
            "email": "notfound@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401