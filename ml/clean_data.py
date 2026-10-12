
import pandas as pd
NON_PRODUCT_CODES = {"DOT", "POST", "M", "D"}


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean retail transactions for gross-sales forecasting.

    Keep records with positive quantities and prices,
    valid product identifiers and dates, and no
    cancellation invoice prefix.
    """

    cleaned = df.copy()

    # Remove cancellations
    cleaned = cleaned[
        ~cleaned["Invoice"].astype(str).str.startswith("C")
    ]

    # Keep positive sales quantities
    cleaned = cleaned[cleaned["Quantity"] > 0]

    # Keep transactions with positive prices
    cleaned = cleaned[cleaned["Price"] > 0]

    # Remove records missing essential information
    cleaned = cleaned.dropna(
        subset=["StockCode", "InvoiceDate"]
    )
    # Exclude known non-product transaction codes
    cleaned = cleaned[
    ~cleaned["StockCode"].astype("string").isin(NON_PRODUCT_CODES)
]
    return cleaned


def get_cleaning_report(df: pd.DataFrame) -> dict:
    """
    Return data-quality counts for the input DataFrame.

    Rule counts can overlap.
    """

    invoice = df["Invoice"].astype("string")

    report = {
        "total_rows": len(df),
        "nonpositive_quantity": int((df["Quantity"] <= 0).sum()),
        "nonpositive_price": int((df["Price"] <= 0).sum()),
        "cancellations": int(
            invoice.str.startswith("C", na=False).sum()
        ),
        "missing_product_code": int(
            df["StockCode"].isna().sum()
        ),
        "missing_invoice_date": int(
            df["InvoiceDate"].isna().sum()
        ),
        
        "non_product_codes": int(
        df["StockCode"]
        .astype("string")
        .isin(NON_PRODUCT_CODES)
        .sum()
        ),
        
    }

    cleaned = clean_sales_data(df)

    report["removed_rows"] = len(df) - len(cleaned)
    report["retained_rows"] = len(cleaned)
    
    return report
