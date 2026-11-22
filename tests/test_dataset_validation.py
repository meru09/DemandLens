
import pandas as pd
import pytest

from backend.dataset_validation import (
    DatasetValidationError,
    inspect_dataset,
)


def test_inspect_valid_csv(tmp_path):
    file_path = tmp_path / "sales.csv"

    pd.DataFrame({
        "Date": ["2025-01-01", "2025-01-02"],
        "Product": ["A101", "A102"],
        "Quantity": [10, 15],
    }).to_csv(file_path, index=False)

    result = inspect_dataset(str(file_path))

    assert result["columns"] == ["Date", "Product", "Quantity"]
    assert len(result["preview"]) == 2
    assert result["sample_row_count"] == 2


def test_reject_unsupported_extension(tmp_path):
    file_path = tmp_path / "sales.txt"
    file_path.write_text("some data")

    with pytest.raises(DatasetValidationError):
        inspect_dataset(str(file_path))


def test_reject_empty_csv(tmp_path):
    file_path = tmp_path / "empty.csv"
    file_path.write_text("")

    with pytest.raises(DatasetValidationError):
        inspect_dataset(str(file_path))


def test_reject_duplicate_columns(tmp_path):
    file_path = tmp_path / "duplicate.csv"
    file_path.write_text(
        "Date,Product,Product\n"
        "2025-01-01,A101,A102\n"
    )

    with pytest.raises(DatasetValidationError):
        inspect_dataset(str(file_path))


def test_reject_unreadable_excel(tmp_path):
    file_path = tmp_path / "invalid.xlsx"
    file_path.write_text("This is not an Excel file")

    with pytest.raises(DatasetValidationError):
        inspect_dataset(str(file_path))


def test_inspect_valid_xlsx(tmp_path):
    file_path = tmp_path / "sales.xlsx"

    pd.DataFrame({
        "Date": ["2025-01-01", "2025-01-02"],
        "Product": ["A101", "A102"],
        "Quantity": [10, 15],
    }).to_excel(file_path, index=False)

    result = inspect_dataset(str(file_path))

    assert result["columns"] == ["Date", "Product", "Quantity"]
    assert len(result["preview"]) == 2
    assert result["sample_row_count"] == 2
