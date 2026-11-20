
from datetime import date

from pydantic import BaseModel


class ForecastResponse(BaseModel):
    stock_code: str
    forecast_date: date
    predicted_units: float
    model: str


class ForecastPoint(BaseModel):
    forecast_date: date
    predicted_units: float


class ForecastHorizonResponse(BaseModel):
    stock_code: str
    forecast_origin: date
    model: str
    horizon_weeks: int
    forecasts: list[ForecastPoint]


class ForecastHorizonMetrics(BaseModel):
    horizon_weeks: int
    evaluation_origins: int
    naive_mae: float | None
    naive_rmse: float | None
    moving_average_mae: float | None
    moving_average_rmse: float | None


class ProductForecastEvaluationResponse(BaseModel):
    stock_code: str
    evaluation_method: str
    metrics: list[ForecastHorizonMetrics]


class ProductSearchResponse(BaseModel):
    query: str
    total_matches: int
    products: list[str]


class DashboardSummaryResponse(BaseModel):
    dataset_start: date
    dataset_end: date
    weeks: int
    total_units_sold: int
    total_products: int
    total_transactions: int
    average_units_per_week: float
