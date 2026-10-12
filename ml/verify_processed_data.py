
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FILE_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_sales.csv"

df = pd.read_csv(FILE_PATH, parse_dates=["InvoiceDate"])

print("--- Processed Dataset Verification ---")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Date range:", df["InvoiceDate"].min(), "to", df["InvoiceDate"].max())
print("Missing dates:", df["InvoiceDate"].isna().sum())

assert len(df) == 1_037_467, "Unexpected row count"
assert len(df.columns) == 8, "Unexpected column count"
assert df["InvoiceDate"].notna().all(), "Missing invoice dates"

print("\nVerification passed!")
