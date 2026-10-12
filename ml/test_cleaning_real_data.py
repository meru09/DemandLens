
from pathlib import Path
import pandas as pd

from ml.clean_data import clean_sales_data

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"

# Load a small sample of real transactions
df = pd.read_excel(
    DATA_PATH,
    sheet_name="Year 2009-2010",
    nrows=1000
)

# Apply our cleaning function
cleaned = clean_sales_data(df)

print("Original rows:", len(df))
print("Cleaned rows:", len(cleaned))
print("Removed rows:", len(df) - len(cleaned))

print("\nFirst five cleaned transactions:")
print(cleaned.head().to_string(index=False))


print("\n--- Cleaning diagnostics ---")

print("Negative or zero quantity:",
      (df["Quantity"] <= 0).sum())

print("Negative or zero price:",
      (df["Price"] <= 0).sum())

print("Cancellation invoices:",
      df["Invoice"].astype(str).str.startswith("C").sum())

print("Missing product codes:",
      df["StockCode"].isna().sum())

print("Missing invoice dates:",
      df["InvoiceDate"].isna().sum())
