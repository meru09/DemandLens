
import pandas as pd

from ml.forecast_baseline import moving_average_forecast


def forecast_product(
    sales: pd.DataFrame,
    stock_code: str
) -> float:
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

