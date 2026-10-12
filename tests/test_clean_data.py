
import pandas as pd

from ml.clean_data import clean_sales_data


def test_clean_sales_data():
    # Arrange: create example transactions
    data = pd.DataFrame({
        "Invoice": ["1001", "C1002", "1003", "1004", "1005"],
        "StockCode": ["P001", "P002", "P003", "P004", None],
        "Quantity": [10, -3, 5, 8, 4],
        "Price": [2.5, 3.0, 0.0, 4.0, 2.0],
        "InvoiceDate": pd.to_datetime([
            "2026-01-01",
            "2026-01-02",
            "2026-01-03",
            "2026-01-04",
            "2026-01-05"
        ])
    })

    # Act: apply our cleaning function
    cleaned = clean_sales_data(data)

    # Assert: verify the expected result
    assert len(cleaned) == 2
    assert cleaned["StockCode"].tolist() == ["P001", "P004"]
    assert (cleaned["Quantity"] > 0).all()
    assert (cleaned["Price"] > 0).all()


def test_cleaning_preserves_original_data():
    # Arrange
    original = pd.DataFrame({
        "Invoice": ["1001", "C1002"],
        "StockCode": ["P001", "P002"],
        "Quantity": [10, -5],
        "Price": [2.5, 3.0],
        "InvoiceDate": pd.to_datetime([
            "2026-01-01",
            "2026-01-02"
        ])
    })

    original_backup = original.copy(deep=True)

    # Act
    cleaned = clean_sales_data(original)

    # Assert
    pd.testing.assert_frame_equal(original, original_backup)
    assert len(cleaned) == 1


def test_missing_values_and_unusual_transactions():
    data = pd.DataFrame({
        "Invoice": ["1001", "1002", "1003", "1004", "1005", "1006"],
        "StockCode": ["P001", "P002", None, "P004", "P005", "P006"],
        "Description": [
            None, "Product B", "Product C",
            "Product D", "Product E", "Product F"
        ],
        "Customer ID": [None, 12345, 12346, 12347, 12348, 12349],
        "Quantity": [5, 3, 8, -4, 0, 7],
        "Price": [2.0, 3.0, 4.0, 0.0, 2.0, 5.0],
        "InvoiceDate": pd.to_datetime([
            "2026-01-01",
            None,
            "2026-01-03",
            "2026-01-04",
            "2026-01-05",
            "2026-01-06"
        ])
    })

    cleaned = clean_sales_data(data)

    assert cleaned["StockCode"].tolist() == ["P001", "P006"]
    assert pd.isna(cleaned.iloc[0]["Description"])
    assert pd.isna(cleaned.iloc[0]["Customer ID"])


from ml.clean_data import clean_sales_data, get_cleaning_report

def test_get_cleaning_report():
    # Arrange
    data = pd.DataFrame({
        "Invoice": ["1001", "C1002", "1003", "1004"],
        "StockCode": ["P001", "P002", "P003", None],
        "Quantity": [10, -5, 4, 3],
        "Price": [2.5, 3.0, 0.0, 2.0],
        "InvoiceDate": pd.to_datetime([
            "2026-01-01",
            "2026-01-02",
            "2026-01-03",
            "2026-01-04"
        ])
    })

    # Act
    report = get_cleaning_report(data)

    # Assert
    assert report["total_rows"] == 4
    assert report["retained_rows"] == 1
    assert report["removed_rows"] == 3

    assert report["nonpositive_quantity"] == 1
    assert report["nonpositive_price"] == 1
    assert report["cancellations"] == 1
    assert report["missing_product_code"] == 1
    assert report["missing_invoice_date"] == 0
    
    
def test_excludes_non_product_codes():
    data = pd.DataFrame({
        "Invoice": ["1001", "1002", "1003", "1004", "1005"],
        "StockCode": ["P001", "POST", "DOT", "M", "D"],
        "Quantity": [10, 1, 1, 2, 1],
        "Price": [2.5, 18.0, 50.0, 3.0, 1.0],
        "InvoiceDate": pd.to_datetime([
            "2026-01-01",
            "2026-01-02",
            "2026-01-03",
            "2026-01-04",
            "2026-01-05"
        ])
    })

    cleaned = clean_sales_data(data)

    assert len(cleaned) == 1
    assert cleaned["StockCode"].tolist() == ["P001"]
