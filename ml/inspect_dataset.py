
from pathlib import Path
import pandas as pd

# Find the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Locate the original dataset
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"

# Open the workbook without loading all its rows
workbook = pd.ExcelFile(DATA_PATH)

print("Dataset:", DATA_PATH.name)
print("Excel sheets:", workbook.sheet_names)


# Inspect the first five rows of each sheet
for sheet in workbook.sheet_names:
    print(f"\n--- {sheet} ---")

    df = pd.read_excel(
        workbook,
        sheet_name=sheet,
        nrows=5
    )

    print(df.to_string(index=False))
    print("\nColumns:", df.columns.tolist())

for sheet in workbook.sheet_names:
    df = pd.read_excel(
        workbook,
        sheet_name=sheet,
        nrows=1000
    )

    print(f"\n--- Data quality: {sheet} ---")
    print("Rows inspected:", len(df))
    print("Missing values:")
    print(df.isna().sum())

    print("Negative quantities:", (df["Quantity"] < 0).sum())
    print("Zero quantities:", (df["Quantity"] == 0).sum())
    print("Unique products:", df["StockCode"].nunique())


# Examine negative-quantity transactions
for sheet in workbook.sheet_names:
    df = pd.read_excel(
        workbook,
        sheet_name=sheet,
        nrows=1000
    )

    negative_sales = df[df["Quantity"] < 0]

    print(f"\n--- Negative quantities: {sheet} ---")

    print(
        negative_sales[
            ["Invoice", "StockCode", "Quantity", "Price"]
        ].head(10).to_string(index=False)
    )

for sheet in workbook.sheet_names:
    df = pd.read_excel(
        workbook,
        sheet_name=sheet,
        nrows=1000
    )

    negative = df[df["Quantity"] < 0]

    not_cancelled = negative[
        ~negative["Invoice"].astype(str).str.startswith("C")
    ]

    print(f"\n--- Cancellation validation: {sheet} ---")
    print("Negative quantity rows:", len(negative))
    print("Negative rows without C invoice:", len(not_cancelled))
    
    
df = pd.read_excel(
    workbook,
    sheet_name="Year 2009-2010",
    nrows=1000
)

exceptions = df[
    (df["Quantity"] < 0)
    & (~df["Invoice"].astype(str).str.startswith("C"))
]

print("\n--- Negative quantity exceptions ---")
print(
    exceptions[
        ["Invoice", "StockCode", "Description",
         "Quantity", "Price", "InvoiceDate"]
    ].to_string(index=False)
)

