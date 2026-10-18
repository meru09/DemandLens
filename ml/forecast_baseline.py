import pandas as pd


def naive_forecast(product_sales: pd.DataFrame) -> float:
    """
    Predict next week's sales using the last observed week.

    Expected columns:
    - InvoiceDate
    - UnitsSold
    """
    if product_sales.empty:
        raise ValueError("Cannot forecast an empty sales history.")

    sorted_sales = product_sales.sort_values("InvoiceDate")

    last_week_sales = sorted_sales["UnitsSold"].iloc[-1]

    return float(last_week_sales)


def calculate_mae(actual, predicted) -> float:
    """
    Calculate Mean Absolute Error between
    actual and predicted sales.
    """
    actual = pd.Series(actual)
    predicted = pd.Series(predicted)

    if len(actual) == 0:
        raise ValueError("Cannot calculate MAE for empty data.")

    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted lengths must match.")

    errors = (actual.to_numpy() - predicted.to_numpy())

    return float(abs(errors).mean())


def create_naive_predictions(product_sales: pd.DataFrame) -> pd.DataFrame:
    """
    Generate one-week-ahead naive predictions
    using the previous week's actual sales.
    """
    sales = product_sales.sort_values("InvoiceDate").copy()

    sales["PredictedUnits"] = sales["UnitsSold"].shift(1)

    return sales.dropna(subset=["PredictedUnits"]).reset_index(drop=True)


def chronological_split(
    product_sales: pd.DataFrame,
    train_ratio: float = 0.8
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split a product's weekly sales into
    chronological training and testing periods.
    """
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1.")

    sales = product_sales.sort_values("InvoiceDate").reset_index(drop=True)

    split_index = int(len(sales) * train_ratio)

    if split_index == 0 or split_index == len(sales):
        raise ValueError("Not enough observations to split the data.")

    train = sales.iloc[:split_index].copy()
    test = sales.iloc[split_index:].copy()

    return train, test


def create_moving_average_predictions(
    product_sales: pd.DataFrame,
    window: int = 3
) -> pd.DataFrame:
    """
    Predict weekly sales using the average of
    the previous `window` weeks.
    """
    if window < 1:
        raise ValueError("Window must be at least 1.")

    sales = product_sales.sort_values("InvoiceDate").copy()

    sales["PredictedUnits"] = (
        sales["UnitsSold"]
        .shift(1)
        .rolling(window=window)
        .mean()
    )

    return sales.dropna(
        subset=["PredictedUnits"]
    ).reset_index(drop=True)


def evaluate_product_baselines(
    product_sales: pd.DataFrame
) -> dict:
    """
    Compare naive and 3-week moving average forecasts
    on the final 20% of one product's history.
    """
    train, test = chronological_split(product_sales)

    # Include the last 3 training weeks for context
    evaluation_data = pd.concat(
        [train.tail(3), test],
        ignore_index=True
    )

    naive = create_naive_predictions(evaluation_data)
    moving = create_moving_average_predictions(
        evaluation_data,
        window=3
    )

    # Keep only the held-out test period
    test_dates = set(test["InvoiceDate"])

    naive = naive[naive["InvoiceDate"].isin(test_dates)]
    moving = moving[moving["InvoiceDate"].isin(test_dates)]

    # Ensure a fair comparison
    assert len(naive) == len(test)
    assert len(moving) == len(test)

    naive_mae = calculate_mae(
        naive["UnitsSold"],
        naive["PredictedUnits"]
    )

    moving_mae = calculate_mae(
        moving["UnitsSold"],
        moving["PredictedUnits"]
    )

    return {
        "naive_mae": naive_mae,
        "moving_average_mae": moving_mae,
        "test_weeks": len(test)
    }


def moving_average_forecast(
    product_sales: pd.DataFrame,
    window: int = 3
) -> float:
    """
    Forecast the next week's sales using
    the most recent `window` weeks.
    """
    if window < 1:
        raise ValueError("Window must be at least 1.")

    sales = product_sales.sort_values("InvoiceDate")

    if len(sales) < window:
        raise ValueError(
            f"At least {window} weeks of sales are required."
        )

    return float(sales["UnitsSold"].tail(window).mean())
