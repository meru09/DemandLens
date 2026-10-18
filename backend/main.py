from fastapi import FastAPI, HTTPException
from functools import lru_cache
import pandas as pd



app = FastAPI(
    title="DemandLens API",
    description="Sales forecasting API for DemandLens",
    version="0.1.0"
)

@lru_cache(maxsize=1)
def load_sales_data():
    return pd.read_csv(
        "data/processed/weekly_sales.csv",
        dtype={"StockCode": str}
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
