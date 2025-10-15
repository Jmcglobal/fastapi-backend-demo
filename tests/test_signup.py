import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from src.main import app
from src.database import get_session
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestSignup:
    """Test suite for signup endpoint"""

    def test_signup_success(self, client: TestClient):
        """Test successful user signup"""
        response = client.post(
            "/api/v1/signup",
            json={
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone_number": "+2348012345678",
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["phone_number"] == "+2348012345678"
        assert "id" in data

    def test_signup_name_validation_only_numbers(self, client: TestClient):
        """Test that name field rejects phone numbers (only digits)"""
        response = client.post(
            "/api/v1/signup",
            json={
                "name": "12345678901",  # Only numbers
                "email": "test@example.com",
                "phone_number": "+2348012345678",
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        assert response.status_code == 422
        assert "Name cannot be only numbers" in str(response.json())

    def test_signup_name_validation_no_alphabet(self, client: TestClient):
        """Test that name must contain at least one alphabet character"""
        response = client.post(
            "/api/v1/signup",
            json={
                "name": "123 456",  # No alphabets
                "email": "test2@example.com",
                "phone_number": "+2348012345679",
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        assert response.status_code == 422
        assert "Name must contain at least one alphabet character" in str(response.json())

    def test_signup_name_with_numbers_valid(self, client: TestClient):
        """Test that name can contain numbers if it also has alphabets"""
        response = client.post(
            "/api/v1/signup",
            json={
                "name": "John Doe 123",  # Valid: has alphabets and numbers
                "email": "john123@example.com",
                "phone_number": "+2348012345670",
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe 123"

    def test_signup_phone_must_start_with_234(self, client: TestClient):
        """Test that phone number must start with +234"""
        response = client.post(
            "/api/v1/signup",
            json={
                "name": "Jane Doe",
                "email": "jane@example.com",
                "phone_number": "+2358012345678",  # Wrong prefix
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        assert response.status_code == 422

    def test_signup_phone_11_digits(self, client: TestClient):
        """Test phone number with exactly 11 digits after +234"""
        response = client.post(
            "/api/v1/signup",
            json={
                "name": "Test User",
                "email": "test11@example.com",
                "phone_number": "+23412345678901",  # 11 digits after +234
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        assert response.status_code == 201

    def test_signup_phone_8_digits(self, client: TestClient):
        """Test phone number with exactly 8 digits after +234 (minimum)"""
        response = client.post(
            "/api/v1/signup",
            json={
                "name": "Test User Eight",
                "email": "test8@example.com",
                "phone_number": "+23412345678",  # 8 digits after +234
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        assert response.status_code == 201

    def test_signup_phone_less_than_8_digits(self, client: TestClient):
        """Test that phone number with less than 8 digits is rejected"""
        response = client.post(
            "/api/v1/signup",
            json={
                "name": "Test User",
                "email": "test7@example.com",
                "phone_number": "+2341234567",  # Only 7 digits after +234
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        assert response.status_code == 422

    def test_signup_phone_more_than_11_digits(self, client: TestClient):
        """Test that phone number with more than 11 digits is rejected"""
        response = client.post(
            "/api/v1/signup",
            json={
                "name": "Test User",
                "email": "test12@example.com",
                "phone_number": "+234123456789012",  # 12 digits after +234
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        assert response.status_code == 422

    def test_signup_duplicate_email(self, client: TestClient):
        """Test that duplicate email is rejected"""
        # First signup
        client.post(
            "/api/v1/signup",
            json={
                "name": "First User",
                "email": "duplicate@example.com",
                "phone_number": "+2348012345671",
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        
        # Second signup with same email
        response = client.post(
            "/api/v1/signup",
            json={
                "name": "Second User",
                "email": "duplicate@example.com",
                "phone_number": "+2348012345672",
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_signup_duplicate_phone(self, client: TestClient):
        """Test that duplicate phone number is rejected"""
        # First signup
        client.post(
            "/api/v1/signup",
            json={
                "name": "First User",
                "email": "user1@example.com",
                "phone_number": "+2348012345673",
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        
        # Second signup with same phone
        response = client.post(
            "/api/v1/signup",
            json={
                "name": "Second User",
                "email": "user2@example.com",
                "phone_number": "+2348012345673",
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        assert response.status_code == 400
        assert "Phone number already registered" in response.json()["detail"]

    def test_signup_invalid_email(self, client: TestClient):
        """Test that invalid email format is rejected"""
        response = client.post(
            "/api/v1/signup",
            json={
                "name": "Test User",
                "email": "invalid-email",
                "phone_number": "+2348012345674",
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        assert response.status_code == 422

    def test_signup_name_too_short(self, client: TestClient):
        """Test that name shorter than 2 characters is rejected"""
        response = client.post(
            "/api/v1/signup",
            json={
                "name": "A",
                "email": "short@example.com",
                "phone_number": "+2348012345675",
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        assert response.status_code == 422

    def test_signup_phone_with_letters(self, client: TestClient):
        """Test that phone number with letters is rejected"""
        response = client.post(
            "/api/v1/signup",
            json={
                "name": "Test User",
                "email": "letters@example.com",
                "phone_number": "+234801234ABC8",
                "country": "Nigeria",
                "state": "Lagos"
            }
        )
        assert response.status_code == 422
