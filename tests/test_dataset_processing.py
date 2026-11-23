
import pandas as pd
import pytest

from backend.dataset_processing import (
    DatasetProcessingError,
    process_uploaded_dataset,
)


def test_process_uploaded_dataset_cleans_and_aggregates(tmp_path):
    file_path = tmp_path / "sales.csv"

    dataframe = pd.DataFrame({
        "Date": [
            "2024-01-01",
            "2024-01-03",
            "2024-01-15",
            None,
            "invalid-date",
            "2024-01-04",
            "2024-01-05",
            "2024-01-06",
            "2024-01-07",
            "2024-01-08",
            "2024-01-22",
        ],
        "Product": [
            "A", "A", "A", "A", "A", None,
            "A", "A", "A", "A", "A",
        ],
        "Quantity": [
            2, 3, 1, 5, 5, 5, None, "invalid", 0, -2, 4,
        ],
    })

    dataframe.to_csv(file_path, index=False)

    result = process_uploaded_dataset(
        file_path,
        date_column="Date",
        product_column="Product",
        quantity_column="Quantity",
    )

    weekly_sales = result["weekly_sales"]
    report = result["cleaning_report"]

    # Three valid records were retained.
    assert report["total_rows"] == 11
    assert report["retained_rows"] == 4
    assert report["removed_rows"] == 7

    # The valid weekly demand is aggregated correctly.
    assert weekly_sales["UnitsSold"].sum() == 10

    # Missing calendar weeks are filled with zero.
    assert len(weekly_sales) == 4
    assert weekly_sales["UnitsSold"].tolist() == [5, 0, 1, 4]

def test_process_uploaded_dataset_rejects_missing_columns(tmp_path):
    file_path = tmp_path / "sales.csv"

    pd.DataFrame({
        "Date": ["2024-01-01"],
        "Product": ["A"],
        "Quantity": [2],
    }).to_csv(file_path, index=False)

    with pytest.raises(DatasetProcessingError):
        process_uploaded_dataset(
            file_path,
            date_column="Date",
            product_column="MissingProduct",
            quantity_column="Quantity",
        )


def test_process_uploaded_dataset_rejects_no_valid_records(tmp_path):
    file_path = tmp_path / "sales.csv"

    pd.DataFrame({
        "Date": ["2024-01-01", "2024-01-02"],
        "Product": ["A", "B"],
        "Quantity": [0, -3],
    }).to_csv(file_path, index=False)

    with pytest.raises(
        DatasetProcessingError,
        match="No valid positive-demand records",
    ):
        process_uploaded_dataset(
            file_path,
            date_column="Date",
            product_column="Product",
            quantity_column="Quantity",
        )


def test_process_uploaded_dataset_rejects_missing_file():
    with pytest.raises(DatasetProcessingError):
        process_uploaded_dataset(
            "missing_sales.csv",
            date_column="Date",
            product_column="Product",
            quantity_column="Quantity",
        )
