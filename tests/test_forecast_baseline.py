
import pandas as pd
import pytest

from ml.forecast_baseline import naive_forecast, calculate_mae, create_naive_predictions, chronological_split, create_moving_average_predictions, evaluate_product_baselines, moving_average_forecast


def test_naive_forecast():
    # Arrange: historical weekly sales
    sales = pd.DataFrame({
        "InvoiceDate": pd.to_datetime([
            "2026-01-18",
            "2026-01-04",
            "2026-01-11"
        ]),
        "UnitsSold": [30, 10, 20]
    })

    # Act: predict next week's sales
    prediction = naive_forecast(sales)

    # Assert: latest week's sales = 30
    assert prediction == 30.0
    
    
def test_naive_forecast_empty_history():
    # Arrange: a product with no sales history
    sales = pd.DataFrame(columns=["InvoiceDate", "UnitsSold"])

    # Act and Assert: forecasting should raise an error
    with pytest.raises(ValueError, match="Cannot forecast an empty sales history"):
        naive_forecast(sales)


def test_calculate_mae():
    # Arrange
    actual = [10, 15, 20]
    predicted = [8, 12, 18]

    # Act
    mae = calculate_mae(actual, predicted)

    # Assert
    assert round(mae, 2) == 2.33


def test_create_naive_predictions():
    # Arrange: dates deliberately out of order
    sales = pd.DataFrame({
        "InvoiceDate": pd.to_datetime([
            "2026-01-18",
            "2026-01-04",
            "2026-01-11",
            "2026-01-25"
        ]),
        "UnitsSold": [8, 10, 15, 12]
    })

    # Act
    result = create_naive_predictions(sales)

    # Assert
    assert len(result) == 3

    assert result["UnitsSold"].tolist() == [15, 8, 12]

    assert result["PredictedUnits"].tolist() == [10, 15, 8]
    
    
def test_chronological_split():
    # Arrange: intentionally unsorted weekly sales
    sales = pd.DataFrame({
        "InvoiceDate": pd.to_datetime([
            "2026-01-25",
            "2026-01-04",
            "2026-02-01",
            "2026-01-11",
            "2026-01-18"
        ]),
        "UnitsSold": [40, 10, 50, 20, 30]
    })

    # Act: use 60% training, 40% testing
    train, test = chronological_split(sales, train_ratio=0.6)

    # Assert: correct number of rows
    assert len(train) == 3
    assert len(test) == 2

    # Training contains the earliest weeks
    assert train["UnitsSold"].tolist() == [10, 20, 30]

    # Testing contains the latest weeks
    assert test["UnitsSold"].tolist() == [40, 50]

    # No future dates appear in training
    assert train["InvoiceDate"].max() < test["InvoiceDate"].min()
    
    
def test_create_moving_average_predictions():
    # Arrange: intentionally unsorted sales history
    sales = pd.DataFrame({
        "InvoiceDate": pd.to_datetime([
            "2026-01-25",
            "2026-01-04",
            "2026-02-01",
            "2026-01-11",
            "2026-01-18"
        ]),
        "UnitsSold": [40, 10, 50, 20, 30]
    })

    # Act
    result = create_moving_average_predictions(
        sales,
        window=3
    )

    # Assert
    assert len(result) == 2

    assert result["UnitsSold"].tolist() == [40, 50]

    assert result["PredictedUnits"].tolist() == [20.0, 30.0]


def test_evaluate_product_baselines():
    # Arrange: 20 weeks with constant sales
    sales = pd.DataFrame({
        "InvoiceDate": pd.date_range(
            start="2026-01-04",
            periods=20,
            freq="W-SUN"
        ),
        "UnitsSold": [10] * 20
    })

    # Act
    results = evaluate_product_baselines(sales)

    # Assert
    assert results["test_weeks"] == 4
    assert results["naive_mae"] == 0.0
    assert results["moving_average_mae"] == 0.0


def test_moving_average_forecast():
    sales = pd.DataFrame({
        "InvoiceDate": pd.to_datetime([
            "2026-01-04",
            "2026-01-11",
            "2026-01-18",
            "2026-01-25"
        ]),
        "UnitsSold": [10, 20, 30, 60]
    })

    prediction = moving_average_forecast(sales, window=3)

    assert prediction == 110 / 3



def test_moving_average_insufficient_history():
    sales = pd.DataFrame({
        "InvoiceDate": pd.to_datetime([
            "2026-01-04",
            "2026-01-11"
        ]),
        "UnitsSold": [20, 30]
    })

    with pytest.raises(
        ValueError,
        match="At least 3 weeks of sales are required"
    ):
        moving_average_forecast(sales, window=3)
