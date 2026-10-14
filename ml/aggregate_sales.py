
import pandas as pd


def aggregate_weekly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate cleaned transactions into weekly product sales.
    """

    weekly = (
        df.groupby([
            "StockCode",
            pd.Grouper(key="InvoiceDate", freq="W-SUN")
        ])["Quantity"]
        .sum()
        .reset_index()
    )

    weekly = weekly.rename(
        columns={"Quantity": "UnitsSold"}
    )

    return weekly

def fill_missing_weeks(weekly: pd.DataFrame) -> pd.DataFrame:
    """
    Create continuous weekly histories for each product.
    Fill missing weeks with zero recorded sales.
    """
    completed = []

    for stock_code, product_data in weekly.groupby("StockCode"):
        product_data = product_data.sort_values("InvoiceDate")

        all_weeks = pd.date_range(
            start=product_data["InvoiceDate"].min(),
            end=product_data["InvoiceDate"].max(),
            freq="W-SUN"
        )

        product_data = (
            product_data.set_index("InvoiceDate")
            .reindex(all_weeks)
        )

        product_data["StockCode"] = stock_code
        product_data["UnitsSold"] = (
        product_data["UnitsSold"].fillna(0).astype("int64")
)
        product_data.index.name = "InvoiceDate"

        completed.append(product_data.reset_index())

    return pd.concat(completed, ignore_index=True)
