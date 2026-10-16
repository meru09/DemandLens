
import pandas as pd


def create_lag_features(
    product_sales: pd.DataFrame
) -> pd.DataFrame:
    """
    Create lag features using the previous
    1, 2, and 3 weeks of sales.
    """
    sales = product_sales.sort_values(
        "InvoiceDate"
    ).copy()

    sales["Lag1"] = sales["UnitsSold"].shift(1)
    sales["Lag2"] = sales["UnitsSold"].shift(2)
    sales["Lag3"] = sales["UnitsSold"].shift(3)


    # Average sales over the previous 3 weeks
    # shift(1) prevents future information leakage
    sales["RollingMean3"] = (
        sales["UnitsSold"]
        .shift(1)
        .rolling(window=3)
        .mean()
    )

    return sales.dropna(
        subset=["Lag1", "Lag2", "Lag3"]
    ).reset_index(drop=True)


def create_global_features(
    weekly_sales: pd.DataFrame
) -> pd.DataFrame:
    """
    Create lag features independently for each product.
    """
    product_features = []

    for stock_code, product_sales in weekly_sales.groupby("StockCode"):

        features = create_lag_features(product_sales)

        if not features.empty:
            product_features.append(features)

    if not product_features:
        return weekly_sales.iloc[0:0].copy()

    global_features = pd.concat(
        product_features,
        ignore_index=True
    )

    return global_features.sort_values(
        ["InvoiceDate", "StockCode"]
    ).reset_index(drop=True)


def global_chronological_split(
    features: pd.DataFrame,
    cutoff_date: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split all products using one shared calendar cutoff.

    Rows before cutoff: training
    Rows on/after cutoff: testing
    """
    cutoff = pd.Timestamp(cutoff_date)

    train = features[
        features["InvoiceDate"] < cutoff
    ].copy()

    test = features[
        features["InvoiceDate"] >= cutoff
    ].copy()

    if train.empty or test.empty:
        raise ValueError(
            "Both training and testing sets must contain data."
        )

    assert train["InvoiceDate"].max() < test["InvoiceDate"].min()

    return train, test
