
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database import Base, get_db
from backend.models import Dataset



def register_user(client, email):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "DemandLens123!",
            "business_name": "Meru Fashion Store",
        },
    )



def upload_test_dataset(client, monkeypatch, tmp_path, email):
    monkeypatch.setattr("backend.business.UPLOAD_DIR", tmp_path)

    registration = register_user(client, email)
    data = registration.json()

    business_id = data["business"]["id"]
    headers = {"Authorization": f"Bearer {data['access_token']}"}

    upload = client.post(
        f"/businesses/{business_id}/datasets/upload",
        headers=headers,
        files={
            "file": (
                "sales.csv",
                b"date,product,quantity\n"
                b"2026-01-01,Product A,10\n"
                b"2026-01-02,Product B,20\n",
                "text/csv",
            )
        },
    )

    assert upload.status_code == 201

    return business_id, headers, upload.json()["dataset_id"]


@pytest.fixture
def test_session_factory():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=test_engine)

    testing_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    yield testing_session_local

    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def test_client(test_session_factory):
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



def test_business_member_can_map_own_dataset(
    test_client, test_session_factory, monkeypatch, tmp_path
):
    business_id, headers, dataset_id = upload_test_dataset(
        test_client, monkeypatch, tmp_path, "mapping@demandlens.com"
    )

    response = test_client.put(
        f"/businesses/{business_id}/datasets/{dataset_id}/mapping",
        headers=headers,
        json={
            "date_column": "date",
            "product_column": "product",
            "quantity_column": "quantity",
        },
    )

    assert response.status_code == 200

    result = response.json()
    assert result["dataset_id"] == dataset_id
    assert result["business_id"] == business_id
    assert result["date_column"] == "date"
    assert result["product_column"] == "product"
    assert result["quantity_column"] == "quantity"
    assert result["status"] == "uploaded"

    with test_session_factory() as db:
        dataset = db.query(Dataset).filter_by(id=dataset_id).first()

        assert dataset.date_column == "date"
        assert dataset.product_column == "product"
        assert dataset.quantity_column == "quantity"



def test_mapping_rejects_nonexistent_column(
    test_client, monkeypatch, tmp_path
):
    business_id, headers, dataset_id = upload_test_dataset(
        test_client, monkeypatch, tmp_path, "missing@demandlens.com"
    )

    response = test_client.put(
        f"/businesses/{business_id}/datasets/{dataset_id}/mapping",
        headers=headers,
        json={
            "date_column": "date",
            "product_column": "unknown_product",
            "quantity_column": "quantity",
        },
    )

    assert response.status_code == 400



def test_mapping_rejects_duplicate_columns(
    test_client, monkeypatch, tmp_path
):
    business_id, headers, dataset_id = upload_test_dataset(
        test_client, monkeypatch, tmp_path, "duplicate@demandlens.com"
    )

    response = test_client.put(
        f"/businesses/{business_id}/datasets/{dataset_id}/mapping",
        headers=headers,
        json={
            "date_column": "date",
            "product_column": "date",
            "quantity_column": "quantity",
        },
    )

    assert response.status_code == 422



def test_user_cannot_map_another_business_dataset(
    test_client, monkeypatch, tmp_path
):
    first_business_id, first_headers, _ = upload_test_dataset(
        test_client, monkeypatch, tmp_path, "first_mapping@demandlens.com"
    )

    _, _, second_dataset_id = upload_test_dataset(
        test_client, monkeypatch, tmp_path, "second_mapping@demandlens.com"
    )

    response = test_client.put(
        f"/businesses/{first_business_id}/datasets/{second_dataset_id}/mapping",
        headers=first_headers,
        json={
            "date_column": "date",
            "product_column": "product",
            "quantity_column": "quantity",
        },
    )

    assert response.status_code == 404



def test_mapping_nonexistent_dataset_returns_404(test_client):
    registration = register_user(
        test_client, "nonexistent_mapping@demandlens.com"
    )
    data = registration.json()

    business_id = data["business"]["id"]
    headers = {"Authorization": f"Bearer {data['access_token']}"}

    response = test_client.put(
        f"/businesses/{business_id}/datasets/999999/mapping",
        headers=headers,
        json={
            "date_column": "date",
            "product_column": "product",
            "quantity_column": "quantity",
        },
    )

    assert response.status_code == 404



def test_mapping_without_token_is_rejected(test_client):
    response = test_client.put(
        "/businesses/1/datasets/1/mapping",
        json={
            "date_column": "date",
            "product_column": "product",
            "quantity_column": "quantity",
        },
    )

    assert response.status_code == 401
