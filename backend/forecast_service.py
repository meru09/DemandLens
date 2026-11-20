
import pandas as pd

from ml.forecast_baseline import (
    evaluate_forecast_horizons,
    moving_average_forecast,
    moving_average_forecast_horizon,
)


def forecast_product(
    sales: pd.DataFrame,
    stock_code: str
) -> dict[str, str | float]:
    product_sales = sales[
        sales["StockCode"] == stock_code
    ].copy()

    if product_sales.empty:
        raise ValueError("Product not found.")

    prediction = moving_average_forecast(
        product_sales,
        window=3
    )

    
    last_week = pd.to_datetime(
        product_sales["InvoiceDate"]
    ).max()

    forecast_week = last_week + pd.Timedelta(weeks=1)

    return {
        "stock_code": stock_code,
        "forecast_date": forecast_week.strftime("%Y-%m-%d"),
        "predicted_units": prediction,
        "model": "moving_average_3"
    }


def forecast_product_horizon(
    sales: pd.DataFrame,
    stock_code: str,
    horizon: int = 3
) -> dict:
    if not 1 <= horizon <= 3:
        raise ValueError("Forecast horizon must be between 1 and 3 weeks.")

    product_sales = sales[
        sales["StockCode"] == stock_code
    ].copy()

    if product_sales.empty:
        raise ValueError("Product not found.")

    product_sales["InvoiceDate"] = pd.to_datetime(
        product_sales["InvoiceDate"]
    )
    product_sales = product_sales.sort_values("InvoiceDate")
    forecast_origin = product_sales["InvoiceDate"].max()
    predictions = moving_average_forecast_horizon(
        product_sales,
        horizon=horizon,
        window=3
    )

    forecasts = [
        {
            "forecast_date": (
                forecast_origin + pd.Timedelta(weeks=step)
            ).strftime("%Y-%m-%d"),
            "predicted_units": prediction
        }
        for step, prediction in enumerate(predictions, start=1)
    ]

    return {
        "stock_code": stock_code,
        "forecast_origin": forecast_origin.strftime("%Y-%m-%d"),
        "model": "moving_average_3_recursive",
        "horizon_weeks": horizon,
        "forecasts": forecasts
    }


def evaluate_product_forecast(
    sales: pd.DataFrame,
    stock_code: str,
    max_horizon: int = 3
) -> dict:
    product_sales = sales[
        sales["StockCode"] == stock_code
    ].copy()

    if product_sales.empty:
        raise ValueError("Product not found.")

    return {
        "stock_code": stock_code,
        "evaluation_method": "rolling_origin_last_20_percent",
        "metrics": evaluate_forecast_horizons(
            product_sales,
            max_horizon=max_horizon,
            train_ratio=0.8,
            window=3
        )
    }

