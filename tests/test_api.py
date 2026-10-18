from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "service": "DemandLens API"
    }


def test_get_products():
    response = client.get("/products")

    assert response.status_code == 200

    data = response.json()

    assert data["total_products"] == 4913
    assert len(data["products"]) == 10
    assert "10002" in data["products"]



def test_product_history():
    response = client.get("/products/10002/history")

    assert response.status_code == 200

    data = response.json()

    assert data["stock_code"] == "10002"
    assert data["total_weeks"] == 73
    assert len(data["history"]) == 73

    first_week = data["history"][0]

    assert first_week["InvoiceDate"] == "2009-12-06"
    assert first_week["UnitsSold"] == 141



def test_product_not_found():
    response = client.get(
        "/products/INVALID123/history"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Product 'INVALID123' not found"
    }
