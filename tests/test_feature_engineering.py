
import pandas as pd

from ml.feature_engineering import create_lag_features, create_global_features, global_chronological_split


def test_create_lag_features():
    # Arrange: deliberately unordered weekly sales
    sales = pd.DataFrame({
        "InvoiceDate": pd.to_datetime([
            "2026-01-25",
            "2026-01-04",
            "2026-02-01",
            "2026-01-11",
            "2026-01-18"
        ]),
        "UnitsSold": [30, 20, 50, 35, 40]
    })

    original_sales = sales.copy(deep=True)

    # Act
    result = create_lag_features(sales)

    # Assert: first 3 weeks cannot have all 3 lags
    assert len(result) == 2

    # Week 4: previous weeks were 40, 35, 20
    assert result.loc[0, "Lag1"] == 40
    assert result.loc[0, "Lag2"] == 35
    assert result.loc[0, "Lag3"] == 20
    assert result.loc[0, "UnitsSold"] == 30

    # Week 5: previous weeks were 30, 40, 35
    assert result.loc[1, "Lag1"] == 30
    assert result.loc[1, "Lag2"] == 40
    assert result.loc[1, "Lag3"] == 35
    assert result.loc[1, "UnitsSold"] == 50

    # Week 4: average of weeks 1, 2, and 3
    assert round(result.loc[0, "RollingMean3"], 2) == 31.67

    # Week 5: average of weeks 2, 3, and 4
    assert result.loc[1, "RollingMean3"] == 35.0

    # No missing rolling averages in the result
    assert result["RollingMean3"].notna().all()


    # Original input must not change
    pd.testing.assert_frame_equal(sales, original_sales)


def test_create_global_features_keeps_products_separate():
    weekly = pd.DataFrame({
        "StockCode": ["A", "B"] * 4,
        "InvoiceDate": pd.to_datetime([
            "2026-01-04", "2026-01-04",
            "2026-01-11", "2026-01-11",
            "2026-01-18", "2026-01-18",
            "2026-01-25", "2026-01-25"
        ]),
        "UnitsSold": [
            10, 100,
            20, 200,
            30, 300,
            40, 400
        ]
    })

    original = weekly.copy(deep=True)

    result = create_global_features(weekly)

    # Each product has one usable row after 3 lags
    assert len(result) == 2

    product_a = result[result["StockCode"] == "A"].iloc[0]
    product_b = result[result["StockCode"] == "B"].iloc[0]

    assert product_a["Lag1"] == 30
    assert product_a["Lag2"] == 20
    assert product_a["Lag3"] == 10
    assert product_a["RollingMean3"] == 20

    assert product_b["Lag1"] == 300
    assert product_b["Lag2"] == 200
    assert product_b["Lag3"] == 100
    assert product_b["RollingMean3"] == 200

    # Original dataset must remain unchanged
    pd.testing.assert_frame_equal(weekly, original)


def test_global_chronological_split():
    data = pd.DataFrame({
        "StockCode": ["A", "B", "A", "B", "A", "B"],
        "InvoiceDate": pd.to_datetime([
            "2026-01-04",
            "2026-01-04",
            "2026-01-11",
            "2026-01-11",
            "2026-01-18",
            "2026-01-18"
        ]),
        "UnitsSold": [10, 100, 20, 200, 30, 300]
    })

    train, test = global_chronological_split(
        data,
        cutoff_date="2026-01-18"
    )

    # Four rows before the cutoff
    assert len(train) == 4

    # Two rows on the cutoff
    assert len(test) == 2

    # No training targets from the future
    assert train["InvoiceDate"].max() < test["InvoiceDate"].min()

    # Both products appear in the test set
    assert set(test["StockCode"]) == {"A", "B"}

    # Original data remains unchanged
    assert len(data) == 6
