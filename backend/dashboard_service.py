import pandas as pd


def summarize_dashboard(
    weekly_sales: pd.DataFrame,
    cleaned_sales: pd.DataFrame
) -> dict:
    if weekly_sales.empty:
        raise ValueError("Weekly sales data is empty.")

    weekly = weekly_sales.copy()
    weekly["InvoiceDate"] = pd.to_datetime(
        weekly["InvoiceDate"],
        errors="raise"
    )
    weekly["UnitsSold"] = pd.to_numeric(
        weekly["UnitsSold"],
        errors="raise"
    )

    week_dates = sorted(weekly["InvoiceDate"].dropna().unique())
    if not week_dates:
        raise ValueError("Weekly sales data has no valid dates.")

    total_units_sold = int(weekly["UnitsSold"].sum())
    total_products = int(weekly["StockCode"].nunique())
    average_units_per_week = total_units_sold / len(week_dates)
    total_transactions = int(cleaned_sales["Invoice"].nunique())

    return {
        "dataset_start": pd.Timestamp(week_dates[0]).date(),
        "dataset_end": pd.Timestamp(week_dates[-1]).date(),
        "weeks": len(week_dates),
        "total_units_sold": total_units_sold,
        "total_products": total_products,
        "total_transactions": total_transactions,
        "average_units_per_week": average_units_per_week
    }
