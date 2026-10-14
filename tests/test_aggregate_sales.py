
import pandas as pd

from ml.aggregate_sales import aggregate_weekly_sales, fill_missing_weeks

def test_aggregate_weekly_sales():
    # Arrange: create sample transactions
    data = pd.DataFrame({
        "StockCode": ["P001", "P001", "P001", "P002"],
        "InvoiceDate": pd.to_datetime([
            "2026-01-05",
            "2026-01-07",
            "2026-01-12",
            "2026-01-06"
        ]),
        "Quantity": [5, 8, 10, 4]
    })

    # Act: aggregate transactions
    result = aggregate_weekly_sales(data)

    # Assert: check expected weekly totals
    p001 = result[result["StockCode"] == "P001"]

    assert len(p001) == 2
    assert p001["UnitsSold"].tolist() == [13, 10]

    p002 = result[result["StockCode"] == "P002"]

    assert len(p002) == 1
    assert p002["UnitsSold"].iloc[0] == 4
    
    
def test_weekly_boundary():
    # Arrange
    data = pd.DataFrame({
        "StockCode": ["P001", "P001"],
        "InvoiceDate": pd.to_datetime([
            "2026-01-11",  # Sunday
            "2026-01-12"   # Monday
        ]),
        "Quantity": [7, 9]
    })

    # Act
    result = aggregate_weekly_sales(data)

    # Assert
    assert len(result) == 2

    assert result["InvoiceDate"].tolist() == [
        pd.Timestamp("2026-01-11"),
        pd.Timestamp("2026-01-18")
    ]

    assert result["UnitsSold"].tolist() == [7, 9]


def test_aggregation_preserves_total_quantity():
    # Arrange
    data = pd.DataFrame({
        "StockCode": ["P001", "P001", "P002", "P002"],
        "InvoiceDate": pd.to_datetime([
            "2026-01-05",
            "2026-01-07",
            "2026-01-06",
            "2026-01-12"
        ]),
        "Quantity": [5, 8, 4, 6]
    })

    # Act
    result = aggregate_weekly_sales(data)

    # Assert
    original_total = data["Quantity"].sum()
    aggregated_total = result["UnitsSold"].sum()

    assert original_total == aggregated_total
    assert aggregated_total == 23
    

def test_fill_missing_weeks():
    # Arrange: Product P001 has no recorded sale on Jan 11
    weekly = pd.DataFrame({
        "StockCode": ["P001", "P001"],
        "InvoiceDate": pd.to_datetime([
            "2026-01-04",
            "2026-01-18"
        ]),
        "UnitsSold": [10, 20]
    })

    # Act
    result = fill_missing_weeks(weekly)

    # Assert
    assert len(result) == 3

    assert result["InvoiceDate"].tolist() == [
        pd.Timestamp("2026-01-04"),
        pd.Timestamp("2026-01-11"),
        pd.Timestamp("2026-01-18")
    ]

    assert result["UnitsSold"].tolist() == [10, 0, 20]

    assert result["UnitsSold"].sum() == 30


def test_fill_missing_weeks_multiple_products():
    # Arrange
    weekly = pd.DataFrame({
        "StockCode": ["P001", "P001", "P002", "P002"],
        "InvoiceDate": pd.to_datetime([
            "2026-01-04",
            "2026-01-18",
            "2026-01-11",
            "2026-01-25"
        ]),
        "UnitsSold": [10, 20, 5, 15]
    })

    # Act
    result = fill_missing_weeks(weekly)

    # Assert
    p001 = result[result["StockCode"] == "P001"]
    p002 = result[result["StockCode"] == "P002"]

    assert p001["UnitsSold"].tolist() == [10, 0, 20]
    assert p002["UnitsSold"].tolist() == [5, 0, 15]

    assert len(result) == 6
    assert result["UnitsSold"].sum() == 50