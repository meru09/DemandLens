
from pathlib import Path

import pandas as pd

from ml.aggregate_sales import (
    aggregate_weekly_sales,
    fill_missing_weeks,
)


ALLOWED_EXTENSIONS = {".csv", ".xlsx"}


class DatasetProcessingError(Exception):
    """Raised when an uploaded dataset cannot be processed."""


def read_uploaded_dataset(file_path: str | Path) -> pd.DataFrame:
    """Read the complete uploaded CSV or the first worksheet of an XLSX file."""

    path = Path(file_path)
    extension = path.suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise DatasetProcessingError(
            "Only CSV and XLSX files are supported."
        )

    if not path.is_file():
        raise DatasetProcessingError("The uploaded file could not be found.")

    try:
        if extension == ".csv":
            dataframe = pd.read_csv(
                path,
                encoding="utf-8-sig",
                skipinitialspace=True,
                low_memory=False,
            )
        else:
            dataframe = pd.read_excel(path, sheet_name=0)

    except Exception as exc:
        raise DatasetProcessingError(
            "The uploaded file could not be read."
        ) from exc

    dataframe.columns = [
        str(column).strip()
        for column in dataframe.columns
    ]

    if dataframe.empty:
        raise DatasetProcessingError(
            "The uploaded file contains no data rows."
        )

    if dataframe.columns.duplicated().any():
        raise DatasetProcessingError(
            "The uploaded file contains duplicate column names."
        )

    return dataframe


def process_uploaded_dataset(
    file_path: str | Path,
    date_column: str,
    product_column: str,
    quantity_column: str,
) -> dict:
    """
    Clean an uploaded dataset and aggregate positive demand by product and week.

    Only positive quantities are included in gross-demand forecasts.
    Exclusion counts in the report may overlap.
    """

    dataframe = read_uploaded_dataset(file_path)

    # Validate the selected column names.
    selected_columns = {
        "date": date_column.strip(),
        "product": product_column.strip(),
        "quantity": quantity_column.strip(),
    }

    missing_columns = [
        column
        for column in selected_columns.values()
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise DatasetProcessingError(
            f"Selected columns were not found: {missing_columns}"
        )

    # Extract and normalize the three selected columns.
    raw_dates = dataframe[selected_columns["date"]]
    raw_products = dataframe[selected_columns["product"]]
    raw_quantities = dataframe[selected_columns["quantity"]]

    dates = pd.to_datetime(raw_dates, errors="coerce")
    products = raw_products.astype("string").str.strip()
    quantities = pd.to_numeric(raw_quantities, errors="coerce")

    # Identify rows that cannot be used for gross-demand forecasting.
    missing_dates = raw_dates.isna()
    invalid_dates = raw_dates.notna() & dates.isna()

    missing_products = products.isna() | products.eq("")
    missing_quantities = raw_quantities.isna()
    invalid_quantities = raw_quantities.notna() & quantities.isna()

    nonpositive_quantities = (
        quantities.notna() & quantities.le(0)
    )

    excluded = (
        missing_dates
        | invalid_dates
        | missing_products
        | missing_quantities
        | invalid_quantities
        | nonpositive_quantities
    )

    # Keep only valid records with positive quantities.
    valid = ~excluded

    cleaned = pd.DataFrame({
        "InvoiceDate": dates[valid],
        "StockCode": products[valid],
        "Quantity": quantities[valid],
    }).reset_index(drop=True)

    if cleaned.empty:
        raise DatasetProcessingError(
            "No valid positive-demand records were found in the uploaded file."
        )

    # Create a transparent cleaning report.
    cleaning_report = {
        "total_rows": int(len(dataframe)),
        "missing_dates": int(missing_dates.sum()),
        "invalid_dates": int(invalid_dates.sum()),
        "missing_products": int(missing_products.sum()),
        "missing_quantities": int(missing_quantities.sum()),
        "invalid_quantities": int(invalid_quantities.sum()),
        "nonpositive_quantities": int(nonpositive_quantities.sum()),
        "removed_rows": int(excluded.sum()),
        "retained_rows": int(valid.sum()),
    }

    # Reuse the existing weekly aggregation pipeline.
    weekly_sales = aggregate_weekly_sales(cleaned)
    weekly_sales = fill_missing_weeks(weekly_sales)

    return {
        "weekly_sales": weekly_sales,
        "cleaning_report": cleaning_report,
    }
