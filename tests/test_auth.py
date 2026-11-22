
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database import Base, get_db
from backend.models import User, Business, BusinessMember
from backend.security import verify_password


@pytest.fixture
def test_session_factory():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    yield TestingSessionLocal

    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def client(test_session_factory):
    def override_get_db():
        db = test_session_factory()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def register_user(client, email="owner@demandlens.com"):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "DemandLens123!",
            "business_name": "Meru Fashion Store",
        },
    )


def test_register_creates_user_business_and_owner(client, test_session_factory):
    response = register_user(client)

    assert response.status_code == 201

    data = response.json()

    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "owner@demandlens.com"
    assert data["business"]["business_name"] == "Meru Fashion Store"

    with test_session_factory() as db:
        user = db.query(User).filter_by(
            email="owner@demandlens.com"
        ).first()

        business = db.query(Business).filter_by(
            business_name="Meru Fashion Store"
        ).first()

        membership = db.query(BusinessMember).filter_by(
            user_id=user.id,
            business_id=business.id,
        ).first()

        assert user is not None
        assert business is not None
        assert membership is not None
        assert membership.role == "owner"
        assert verify_password("DemandLens123!", user.password_hash)


def test_duplicate_registration_is_rejected(client):
    first_response = register_user(client)
    second_response = register_user(client)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_with_correct_credentials(client):
    register_user(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "owner@demandlens.com",
            "password": "DemandLens123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["user"]["email"] == "owner@demandlens.com"


def test_login_with_wrong_password_is_rejected(client):
    register_user(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "owner@demandlens.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_me_with_valid_token(client):
    registration = register_user(client)
    token = registration.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "owner@demandlens.com"


def test_me_without_token_is_rejected(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_with_invalid_token_is_rejected(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401


def test_user_can_access_own_business(client):
    registration = register_user(client)
    data = registration.json()

    response = client.get(
        f"/businesses/{data['business']['id']}",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "business_id": data["business"]["id"],
        "business_name": "Meru Fashion Store",
    }


def test_user_cannot_access_another_users_business(client):
    first = register_user(client, email="first@demandlens.com")
    second = register_user(client, email="second@demandlens.com")

    first_data = first.json()
    second_data = second.json()

    response = client.get(
        f"/businesses/{second_data['business']['id']}",
        headers={"Authorization": f"Bearer {first_data['access_token']}"},
    )

    assert response.status_code == 404


def test_nonexistent_business_returns_404(client):
    registration = register_user(client)
    token = registration.json()["access_token"]

    response = client.get(
        "/businesses/999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_business_details_without_token_is_rejected(client):
    registration = register_user(client)
    business_id = registration.json()["business"]["id"]

    response = client.get(f"/businesses/{business_id}")

    assert response.status_code == 401


def test_business_list_only_returns_current_users_businesses(client):
    first = register_user(client, email="first@demandlens.com")
    register_user(client, email="second@demandlens.com")

    token = first.json()["access_token"]

    response = client.get(
        "/businesses",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["business_name"] == "Meru Fashion Store"
    assert data[0]["role"] == "owner"
