
from pathlib import Path
import pandas as pd
from ml.clean_data import clean_sales_data, get_cleaning_report


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"


def load_dataset() -> pd.DataFrame:
    """Load and combine both years of retail transactions."""

    print("Loading Year 2009-2010...")
    first_year = pd.read_excel(
        DATA_PATH,
        sheet_name="Year 2009-2010"
    )

    print("Loading Year 2010-2011...")
    second_year = pd.read_excel(
        DATA_PATH,
        sheet_name="Year 2010-2011"
    )

    combined = pd.concat(
        [first_year, second_year],
        ignore_index=True
    )

    return combined


if __name__ == "__main__":
    df = load_dataset()

    print("\n--- Dataset Summary ---")
    print("Total rows:", len(df))
    print("Total columns:", len(df.columns))
    print("Date range:", df["InvoiceDate"].min(), "to", df["InvoiceDate"].max())
    print("Unique stock codes:", df["StockCode"].nunique())
    print("Exact duplicate rows:", df.duplicated().sum())
    
    print("\n--- Full Cleaning Report ---")

    report = get_cleaning_report(df)

    for key, value in report.items():
        print(f"{key}: {value:,}")

    cleaned = clean_sales_data(df)

    retention_rate = len(cleaned) / len(df) * 100

    print(f"\nRetention rate: {retention_rate:.2f}%")
    print("Cleaned date range:",
          cleaned["InvoiceDate"].min(),
          "to",
          cleaned["InvoiceDate"].max())


    # Create the processed-data directory if necessary
    output_dir = PROJECT_ROOT / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save cleaned transactions
    output_path = output_dir / "cleaned_sales.csv"

    cleaned.to_csv(output_path, index=False)

    print("\n--- Export Complete ---")
    print("Saved to:", output_path)
    print("Exported rows:", len(cleaned))

