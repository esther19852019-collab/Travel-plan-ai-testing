import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate

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