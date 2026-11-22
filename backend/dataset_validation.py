
import csv
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

ALLOWED_EXTENSIONS = {".csv", ".xlsx"}


class DatasetValidationError(Exception):
    pass


def read_original_headers(path: Path, extension: str) -> list:
    if extension == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file)
            return next(reader, [])

    workbook = load_workbook(
        path,
        read_only=True,
        data_only=True,
    )

    try:
        worksheet = workbook.active
        return list(
            next(
                worksheet.iter_rows(
                    min_row=1,
                    max_row=1,
                    values_only=True,
                ),
                [],
            )
        )
    finally:
        workbook.close()


def inspect_dataset(file_path: str) -> dict:
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise DatasetValidationError(
            "Only CSV and XLSX files are supported."
        )

    try:
        original_headers = read_original_headers(path, extension)

        columns = [
            str(column).strip() if column is not None else ""
            for column in original_headers
        ]

        if not columns or any(not column for column in columns):
            raise DatasetValidationError(
                "The file contains missing or invalid column names."
            )

        if len(columns) != len(set(columns)):
            raise DatasetValidationError(
                "The file contains duplicate column names."
            )

        if extension == ".csv":
            dataframe = pd.read_csv(path, nrows=1000)
        else:
            dataframe = pd.read_excel(path, nrows=1000)

    except DatasetValidationError:
        raise
    except Exception as exc:
        raise DatasetValidationError(
            "The uploaded file could not be read. "
            "Please check that it is a valid CSV or Excel file."
        ) from exc

    if dataframe.empty:
        raise DatasetValidationError(
            "The uploaded file contains no data rows."
        )

    return {
        "columns": columns,
        "preview": (
            dataframe.fillna("")
            .astype(str)
            .head(5)
            .to_dict(orient="records")
        ),
        "sample_row_count": len(dataframe),
    }
