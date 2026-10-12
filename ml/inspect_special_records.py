
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"

df = pd.read_excel(
    DATA_PATH,
    sheet_name="Year 2009-2010",
    nrows=10000
)

print("--- Special stock codes ---")

special_codes = ["POST", "D", "M", "BANK CHARGES", "DOT", "C2"]

special = df[
    df["StockCode"].astype(str).isin(special_codes)
]

print(
    special[
        ["StockCode", "Description", "Quantity", "Price"]
    ].head(15).to_string(index=False)
)

print("\nSpecial-code rows:", len(special))

print("\n--- Duplicate records ---")
print("Exact duplicate rows:", df.duplicated().sum())


print("\n--- All suspected non-product codes ---")

suspected = df[
    df["StockCode"].astype(str).str.fullmatch(
        r"[A-Za-z ]+",
        na=False
    )
]

print(
    suspected.groupby(["StockCode", "Description"], dropna=False)
    .size()
    .reset_index(name="Rows")
    .sort_values("Rows", ascending=False)
    .to_string(index=False)
)

