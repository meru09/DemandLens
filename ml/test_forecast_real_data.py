
import pandas as pd

from ml.forecast_baseline import (
    naive_forecast,
    calculate_mae,
    create_naive_predictions,
    chronological_split,
    create_moving_average_predictions,
)

# Load completed weekly sales
weekly = pd.read_csv(
    "data/processed/weekly_sales.csv",
    dtype={"StockCode": str},
    parse_dates=["InvoiceDate"]
)

# Select one product
product_code = "10002"

product_sales = weekly[
    weekly["StockCode"] == product_code
].copy()

# Generate next week's forecast
prediction = naive_forecast(product_sales)

last_date = product_sales["InvoiceDate"].max()
next_week = last_date + pd.Timedelta(weeks=1)

print("\n--- DemandLens First Forecast ---")
print("Product:", product_code)
print("Historical weeks:", len(product_sales))
print("Last recorded week:", last_date.date())
print("Last recorded sales:", prediction)
print("Forecast week:", next_week.date())
print("Predicted units:", prediction)


print("\n--- DemandLens Baseline Evaluation ---")

# Split historical sales into past and future periods
train, test = chronological_split(
    product_sales,
    train_ratio=0.8
)

# Include the final training week as the starting point
evaluation_data = pd.concat([
    train.tail(1),
    test
], ignore_index=True)

# Predict each test week using the previous week's actual sales
predictions = create_naive_predictions(evaluation_data)

# Calculate forecasting error
mae = calculate_mae(
    predictions["UnitsSold"],
    predictions["PredictedUnits"]
)

print("Training weeks:", len(train))
print("Testing weeks:", len(test))
print("Predictions evaluated:", len(predictions))
print("Baseline MAE:", round(mae, 2))

print("\n--- First 5 Predictions ---")
print(
    predictions[
        ["InvoiceDate", "UnitsSold", "PredictedUnits"]
    ].head().to_string(index=False)
)


print("\n--- Baseline Model Comparison ---")

# Include the last 3 training weeks as context
evaluation_data = pd.concat([
    train.tail(3),
    test
], ignore_index=True)

# Generate predictions for the same 15 test weeks
naive_results = create_naive_predictions(evaluation_data)
moving_results = create_moving_average_predictions(
    evaluation_data,
    window=3
)

# Keep only predictions for the held-out test dates
test_dates = set(test["InvoiceDate"])

naive_results = naive_results[
    naive_results["InvoiceDate"].isin(test_dates)
]

moving_results = moving_results[
    moving_results["InvoiceDate"].isin(test_dates)
]

# Verify a fair comparison
assert len(naive_results) == len(test)
assert len(moving_results) == len(test)

assert (
    naive_results["InvoiceDate"].tolist()
    == moving_results["InvoiceDate"].tolist()
)

# Calculate MAE for both models
naive_mae = calculate_mae(
    naive_results["UnitsSold"],
    naive_results["PredictedUnits"]
)

moving_mae = calculate_mae(
    moving_results["UnitsSold"],
    moving_results["PredictedUnits"]
)

print("Test weeks:", len(test))
print("Naive MAE:", round(naive_mae, 2))
print("Moving Average MAE:", round(moving_mae, 2))

if moving_mae < naive_mae:
    print("Winner: 3-week Moving Average")
elif naive_mae < moving_mae:
    print("Winner: Naive Baseline")
else:
    print("Result: Tie")


print("\n--- Product History Lengths ---")

history_lengths = (
    weekly.groupby("StockCode")
    .size()
)

print("Total products:", len(history_lengths))
print("Minimum weeks:", history_lengths.min())
print("Median weeks:", history_lengths.median())
print("Maximum weeks:", history_lengths.max())

print(
    "Products with at least 20 weeks:",
    (history_lengths >= 20).sum()
)

print(
    "Products with fewer than 20 weeks:",
    (history_lengths < 20).sum()
)
