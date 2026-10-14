
from pathlib import Path
import pandas as pd

from ml.aggregate_sales import aggregate_weekly_sales, fill_missing_weeks

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT / "data" / "processed" / "cleaned_sales.csv"
)

# Load cleaned transactions
df = pd.read_csv(
    DATA_PATH,
    parse_dates=["InvoiceDate"],
    dtype={"StockCode": "string"}
)

print("--- Original Cleaned Data ---")
print("Transactions:", len(df))
print("Total units sold:", df["Quantity"].sum())

# Aggregate by product and week
weekly = aggregate_weekly_sales(df)

print("\n--- Weekly Aggregated Data ---")
print("Product-week records:", len(weekly))
print("Unique products:", weekly["StockCode"].nunique())
print("Total units sold:", weekly["UnitsSold"].sum())

print("\n--- First 10 Rows ---")
print(weekly.head(10).to_string(index=False))

# Verify that aggregation preserved total sales
assert df["Quantity"].sum() == weekly["UnitsSold"].sum()

print("\nAggregation verification passed!")


print("\n--- Product 10002: Weekly Sales History ---")

product = weekly[
    weekly["StockCode"] == "10002"
].copy()

product = product.sort_values("InvoiceDate")

# All calendar weeks between first and last observed sale
all_weeks = pd.date_range(
    start=product["InvoiceDate"].min(),
    end=product["InvoiceDate"].max(),
    freq="W-SUN"
)

observed_weeks = product["InvoiceDate"]

missing_weeks = all_weeks.difference(observed_weeks)

print("Observed weeks:", len(observed_weeks))
print("Calendar weeks:", len(all_weeks))
print("Missing weeks:", len(missing_weeks))

print("\nFirst 10 missing weeks:")
print(missing_weeks[:10])


print("\n--- Weekly Coverage Across Products ---")

coverage = weekly.groupby("StockCode").agg(
    first_week=("InvoiceDate", "min"),
    last_week=("InvoiceDate", "max"),
    observed_weeks=("InvoiceDate", "nunique")
)

coverage["calendar_weeks"] = (
    (coverage["last_week"] - coverage["first_week"]).dt.days // 7
) + 1

coverage["missing_weeks"] = (
    coverage["calendar_weeks"] - coverage["observed_weeks"]
)

coverage["coverage_rate"] = (
    coverage["observed_weeks"] / coverage["calendar_weeks"]
)

print("Products analyzed:", len(coverage))
print("Median coverage:", f"{coverage['coverage_rate'].median():.2%}")
print("Products with no missing weeks:",
      (coverage["missing_weeks"] == 0).sum())
print("Products with missing weeks:",
      (coverage["missing_weeks"] > 0).sum())

print("\n--- Coverage Distribution ---")
print(coverage["coverage_rate"].describe())


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


print("\n--- Complete Weekly Sales Histories ---")

# Fill missing weeks independently for each product
completed_weekly = fill_missing_weeks(weekly)

print("Original product-week rows:", len(weekly))
print("Completed product-week rows:", len(completed_weekly))

added_rows = len(completed_weekly) - len(weekly)

print("Missing weeks filled:", added_rows)

print(
    "Zero-sales weeks:",
    (completed_weekly["UnitsSold"] == 0).sum()
)

print(
    "Total units after filling:",
    completed_weekly["UnitsSold"].sum()
)

# Verify no sales quantities were lost
assert (
    weekly["UnitsSold"].sum()
    == completed_weekly["UnitsSold"].sum()
)

# Verify product count remains unchanged
assert (
    weekly["StockCode"].nunique()
    == completed_weekly["StockCode"].nunique()
)

print("\nWeekly completion verification passed!")


# Export completed weekly sales for forecasting
output_path = "data/processed/weekly_sales.csv"

completed_weekly.to_csv(output_path, index=False)

print(f"\nWeekly sales exported to: {output_path}")

# Reload the file to verify the saved dataset
saved_weekly = pd.read_csv(
    output_path,
    dtype={"StockCode": str},
    parse_dates=["InvoiceDate"]
)

assert len(saved_weekly) == len(completed_weekly)
assert saved_weekly["StockCode"].nunique() == 4913
assert saved_weekly["UnitsSold"].sum() == 11403162
assert saved_weekly["UnitsSold"].isna().sum() == 0

print("Export verification passed!")
print("Saved rows:", len(saved_weekly))
print("Saved products:", saved_weekly["StockCode"].nunique())
print("Saved total units:", saved_weekly["UnitsSold"].sum())
