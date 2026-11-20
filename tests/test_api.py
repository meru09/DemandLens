from fastapi.testclient import TestClient
from backend.main import app
import pandas as pd
from unittest.mock import patch


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



def test_product_forecast():
    response = client.get(
        "/products/10002/forecast"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["stock_code"] == "10002"
    assert data["forecast_date"] == "2011-05-01"
    assert data["predicted_units"] == 21.0
    assert data["model"] == "moving_average_3"



def test_forecast_invalid_product():
    response = client.get(
        "/products/INVALID123/forecast"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product not found."



def test_forecast_insufficient_history():
    sales = pd.DataFrame({
        "StockCode": ["TEST01", "TEST01"],
        "InvoiceDate": [
            "2026-01-04",
            "2026-01-11"
        ],
        "UnitsSold": [20, 30]
    })

    with patch(
        "backend.main.load_sales_data",
        return_value=sales
    ):
        response = client.get(
            "/products/TEST01/forecast"
        )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "At least 3 weeks of sales are required."
    )


def test_search_products():
    response = client.get(
        "/products/search",
        params={"q": "10002", "limit": 5}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "10002"
    assert data["total_matches"] >= 1
    assert "10002" in data["products"]
    assert len(data["products"]) <= 5


def test_three_week_forecast_preserves_existing_one_week_result():
    one_week = client.get("/products/10002/forecast")
    response = client.get("/products/10002/forecasts")

    assert one_week.status_code == 200
    assert response.status_code == 200

    data = response.json()
    assert data["stock_code"] == "10002"
    assert data["forecast_origin"] == "2011-04-24"
    assert data["model"] == "moving_average_3_recursive"
    assert data["horizon_weeks"] == 3
    assert [point["forecast_date"] for point in data["forecasts"]] == [
        "2011-05-01",
        "2011-05-08",
        "2011-05-15"
    ]
    assert data["forecasts"][0]["predicted_units"] == (
        one_week.json()["predicted_units"]
    )


def test_three_week_forecast_rejects_unsupported_horizon():
    response = client.get(
        "/products/10002/forecasts",
        params={"horizon": 4}
    )

    assert response.status_code == 422


def test_product_forecast_evaluation_reports_three_leads():
    response = client.get("/products/10002/evaluation")

    assert response.status_code == 200
    data = response.json()
    assert data["stock_code"] == "10002"
    assert data["evaluation_method"] == (
        "rolling_origin_last_20_percent"
    )
    assert [metric["horizon_weeks"] for metric in data["metrics"]] == [
        1,
        2,
        3
    ]
    assert all(
        metric["evaluation_origins"] > 0
        for metric in data["metrics"]
    )


def test_dashboard_summary_uses_real_aggregates():
    weekly_sales = pd.DataFrame({
        "StockCode": ["A", "A", "B"],
        "InvoiceDate": [
            "2026-01-04",
            "2026-01-11",
            "2026-01-11"
        ],
        "UnitsSold": [10, 20, 5]
    })
    cleaned_sales = pd.DataFrame({
        "Invoice": ["100", "101", "101", "102"]
    })

    with (
        patch(
            "backend.main.load_sales_data",
            return_value=weekly_sales
        ),
        patch(
            "backend.main.load_cleaned_sales_data",
            return_value=cleaned_sales
        )
    ):
        response = client.get("/dashboard/summary")

    assert response.status_code == 200
    assert response.json() == {
        "dataset_start": "2026-01-04",
        "dataset_end": "2026-01-11",
        "weeks": 2,
        "total_units_sold": 35,
        "total_products": 2,
        "total_transactions": 3,
        "average_units_per_week": 17.5
    }
