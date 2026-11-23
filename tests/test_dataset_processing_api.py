
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database import Base, get_db
from backend.models import DatasetProcessing


@pytest.fixture
def test_session_factory():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=test_engine)

    testing_session = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    yield testing_session

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


def create_mapped_dataset(
    client,
    monkeypatch,
    tmp_path,
    email="owner@example.com",
):
    monkeypatch.setattr(
        "backend.business.UPLOAD_DIR",
        tmp_path / "uploads",
    )
    monkeypatch.setattr(
        "backend.business.PROJECT_ROOT",
        tmp_path,
    )

    registration = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "DemandLens123!",
            "business_name": "Test Store",
        },
    )

    assert registration.status_code == 201

    data = registration.json()
    business_id = data["business"]["id"]
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

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

    dataset_id = upload.json()["dataset_id"]

    mapping = client.put(
        f"/businesses/{business_id}/datasets/{dataset_id}/mapping",
        headers=headers,
        json={
            "date_column": "date",
            "product_column": "product",
            "quantity_column": "quantity",
        },
    )

    assert mapping.status_code == 200

    return business_id, dataset_id, headers


def test_business_can_process_own_dataset(
    client,
    test_session_factory,
    monkeypatch,
    tmp_path,
):
    business_id, dataset_id, headers = create_mapped_dataset(
        client,
        monkeypatch,
        tmp_path,
    )

    response = client.post(
        f"/businesses/{business_id}/datasets/{dataset_id}/process",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "processed"
    assert data["total_rows"] == 2
    assert data["retained_rows"] == 2
    assert data["removed_rows"] == 0

    with test_session_factory() as db:
        processing = (
            db.query(DatasetProcessing)
            .filter_by(dataset_id=dataset_id)
            .first()
        )

        assert processing is not None
        assert processing.business_id == business_id
        assert processing.retained_rows == 2

        from pathlib import Path
        assert Path(processing.processed_file_path).is_file()


def test_processing_requires_column_mapping(
    client,
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        "backend.business.UPLOAD_DIR",
        tmp_path / "uploads",
    )

    registration = client.post(
        "/auth/register",
        json={
            "email": "unmapped@example.com",
            "password": "DemandLens123!",
            "business_name": "Unmapped Store",
        },
    )

    data = registration.json()
    business_id = data["business"]["id"]
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    upload = client.post(
        f"/businesses/{business_id}/datasets/upload",
        headers=headers,
        files={
            "file": (
                "sales.csv",
                b"date,product,quantity\n"
                b"2026-01-01,A,10\n",
                "text/csv",
            )
        },
    )

    dataset_id = upload.json()["dataset_id"]

    response = client.post(
        f"/businesses/{business_id}/datasets/{dataset_id}/process",
        headers=headers,
    )

    assert response.status_code == 400
    assert "Map the date" in response.json()["detail"]


def test_user_cannot_process_another_business_dataset(
    client,
    monkeypatch,
    tmp_path,
):
    first_business_id, dataset_id, first_headers = create_mapped_dataset(
        client,
        monkeypatch,
        tmp_path,
        email="first@example.com",
    )

    second_registration = client.post(
        "/auth/register",
        json={
            "email": "second@example.com",
            "password": "DemandLens123!",
            "business_name": "Second Store",
        },
    )

    second_data = second_registration.json()
    second_business_id = second_data["business"]["id"]
    second_headers = {
        "Authorization": f"Bearer {second_data['access_token']}"
    }

    response = client.post(
        f"/businesses/{second_business_id}/datasets/{dataset_id}/process",
        headers=second_headers,
    )

    assert response.status_code == 404


def test_processing_without_token_is_rejected(
    client,
    monkeypatch,
    tmp_path,
):
    business_id, dataset_id, headers = create_mapped_dataset(
        client,
        monkeypatch,
        tmp_path,
    )

    response = client.post(
        f"/businesses/{business_id}/datasets/{dataset_id}/process",
    )

    assert response.status_code == 401


def test_reprocessing_updates_existing_result(
    client,
    test_session_factory,
    monkeypatch,
    tmp_path,
):
    business_id, dataset_id, headers = create_mapped_dataset(
        client,
        monkeypatch,
        tmp_path,
    )

    endpoint = (
        f"/businesses/{business_id}/datasets/{dataset_id}/process"
    )

    first_response = client.post(endpoint, headers=headers)
    assert first_response.status_code == 200

    with test_session_factory() as db:
        first_record = (
            db.query(DatasetProcessing)
            .filter_by(dataset_id=dataset_id)
            .first()
        )
        first_path = first_record.processed_file_path

    second_response = client.post(endpoint, headers=headers)
    assert second_response.status_code == 200

    with test_session_factory() as db:
        records = (
            db.query(DatasetProcessing)
            .filter_by(dataset_id=dataset_id)
            .all()
        )

        assert len(records) == 1

        second_path = records[0].processed_file_path

        assert second_path != first_path

        from pathlib import Path
        assert Path(second_path).is_file()
        assert not Path(first_path).exists()
