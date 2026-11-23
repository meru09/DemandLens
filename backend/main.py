from fastapi import FastAPI, HTTPException, Query
from functools import lru_cache
from pathlib import Path
import pandas as pd
from backend.dashboard_service import summarize_dashboard
from backend.forecast_service import (
    evaluate_product_forecast,
    forecast_product,
    forecast_product_horizon,
)
from backend.schemas import (
    DashboardSummaryResponse,
    ForecastHorizonResponse,
    ForecastResponse,
    ProductForecastEvaluationResponse,
    ProductSearchResponse,
)
from fastapi.middleware.cors import CORSMiddleware
from backend.auth import router as auth_router
from backend.business import router as business_router
from backend.database import Base, engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]

app = FastAPI(
    title="DemandLens API",
    description="Sales forecasting API for DemandLens",
    version="0.1.0"
)

@app.on_event("startup")
def create_database_tables():
    Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(business_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET ,POST"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def load_sales_data():
    return pd.read_csv(
        PROJECT_ROOT / "data/processed/weekly_sales.csv",
        dtype={"StockCode": str}
    )


@lru_cache(maxsize=1)
def load_cleaned_sales_data():
    return pd.read_csv(
        PROJECT_ROOT / "data/processed/cleaned_sales.csv",
        dtype={
            "Invoice": "string",
            "StockCode": str
        },
        parse_dates=["InvoiceDate"],
        low_memory=False
    )



@app.get("/")
def home():
    return {
        "message": "Welcome to DemandLens API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "DemandLens API"
    }


@app.get("/products")
def get_products():
    sales = load_sales_data()

    products = sorted(sales["StockCode"].unique())

    return {
        "total_products": len(products),
        "products": products[:10]
    }


@app.get(
    "/products/search",
    response_model=ProductSearchResponse
)
def search_products(
    q: str = Query(min_length=1, max_length=64),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    query = q.strip()
    if not query:
        raise HTTPException(
            status_code=422,
            detail="Search query must not be empty."
        )

    products = sorted(load_sales_data()["StockCode"].dropna().unique())
    matches = [
        product
        for product in products
        if query.casefold() in product.casefold()
    ]

    return {
        "query": query,
        "total_matches": len(matches),
        "products": matches[offset:offset + limit]
    }


@app.get(
    "/dashboard/summary",
    response_model=DashboardSummaryResponse
)
def get_dashboard_summary():
    return summarize_dashboard(
        load_sales_data(),
        load_cleaned_sales_data()
    )


@app.get("/products/{stock_code}/history")
def get_product_history(stock_code: str):
    sales = load_sales_data()

    product_sales = sales[
        sales["StockCode"] == stock_code
    ].copy()

    if product_sales.empty:
       raise HTTPException(
        status_code=404,
        detail=f"Product '{stock_code}' not found"
    )


    return {
        "stock_code": stock_code,
        "total_weeks": len(product_sales),
        "history": product_sales[
            ["InvoiceDate", "UnitsSold"]
        ].to_dict(orient="records")

    }



@app.get(
    "/products/{stock_code}/forecast",
    response_model=ForecastResponse
)
def get_product_forecast(stock_code: str):
    sales = load_sales_data()

    try:
        result = forecast_product(
            sales,
            stock_code
        )
        return result


    except ValueError as error:
        message = str(error)

        if message == "Product not found.":
            raise HTTPException(
                status_code=404,
                detail=message
            )

        raise HTTPException(
            status_code=422,
            detail=message
        )


@app.get(
    "/products/{stock_code}/forecasts",
    response_model=ForecastHorizonResponse
)
def get_product_forecasts(
    stock_code: str,
    horizon: int = Query(default=3, ge=1, le=3)
):
    try:
        return forecast_product_horizon(
            load_sales_data(),
            stock_code,
            horizon
        )
    except ValueError as error:
        message = str(error)

        if message == "Product not found.":
            raise HTTPException(
                status_code=404,
                detail=message
            )

        raise HTTPException(
            status_code=422,
            detail=message
        )


@app.get(
    "/products/{stock_code}/evaluation",
    response_model=ProductForecastEvaluationResponse
)
def get_product_forecast_evaluation(stock_code: str):
    try:
        return evaluate_product_forecast(
            load_sales_data(),
            stock_code
        )
    except ValueError as error:
        message = str(error)

        if message == "Product not found.":
            raise HTTPException(
                status_code=404,
                detail=message
            )

        raise HTTPException(
            status_code=422,
            detail=message
        )

