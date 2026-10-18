
from datetime import date

from pydantic import BaseModel


class ForecastResponse(BaseModel):
    stock_code: str
    forecast_date: date
    predicted_units: float
    model: str
