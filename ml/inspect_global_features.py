
import pandas as pd

from ml.feature_engineering import create_global_features, global_chronological_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error



# Load our prepared weekly sales
weekly_sales = pd.read_csv(
    "data/processed/weekly_sales.csv",
    dtype={"StockCode": str},
    parse_dates=["InvoiceDate"]
)

# Generate lag features independently for each product
features = create_global_features(weekly_sales)

print("\n--- Global Feature Dataset ---")
print("Total examples:", len(features))
print("Unique products:", features["StockCode"].nunique())
print("First date:", features["InvoiceDate"].min())
print("Last date:", features["InvoiceDate"].max())

# Count available examples by calendar month
monthly_counts = (
    features.groupby(
        features["InvoiceDate"].dt.to_period("M")
    )
    .size()
)

print("\n--- Monthly Example Counts ---")
print(monthly_counts.to_string())


# Split using one shared cutoff date
cutoff_date = "2011-09-01"

train, test = global_chronological_split(
    features,
    cutoff_date=cutoff_date
)

print("\n--- Global Chronological Split ---")
print("Cutoff date:", cutoff_date)
print("Training examples:", len(train))
print("Testing examples:", len(test))

print("Training products:", train["StockCode"].nunique())
print("Testing products:", test["StockCode"].nunique())

print("Last training date:", train["InvoiceDate"].max())
print("First testing date:", test["InvoiceDate"].min())

# Products appearing in both periods
shared_products = (
    set(train["StockCode"])
    & set(test["StockCode"])
)

print("Products in both periods:", len(shared_products))

assert train["InvoiceDate"].max() < test["InvoiceDate"].min()
assert len(train) + len(test) == len(features)


# Prepare global ML inputs
feature_columns = [
    "Lag1",
    "Lag2",
    "Lag3",
    "RollingMean3"
]

X_train = train[feature_columns]
y_train = train["UnitsSold"]

X_test = test[feature_columns]
y_test = test["UnitsSold"]

print("\n--- Global ML Inputs ---")
print("X_train shape:", X_train.shape)
print("y_train shape:", y_train.shape)
print("X_test shape:", X_test.shape)
print("y_test shape:", y_test.shape)

print("Missing training values:", X_train.isna().sum().sum())
print("Missing testing values:", X_test.isna().sum().sum())

assert len(X_train) == len(y_train)
assert len(X_test) == len(y_test)
assert not X_train.isna().any().any()
assert not X_test.isna().any().any()



# Train our first global Random Forest
global_model = RandomForestRegressor(
    n_estimators=50,
    max_depth=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)

print("\n--- Training Global Random Forest ---")
print("Training examples:", len(X_train))

global_model.fit(X_train, y_train)

print("Global Random Forest trained successfully!")

# Generate predictions for the test period
global_predictions = global_model.predict(X_test)

print("Predictions generated:", len(global_predictions))
print("First 5 predictions:", global_predictions[:5])


# Evaluate the global Random Forest
global_mae = mean_absolute_error(
    y_test,
    global_predictions
)

print("\n--- Global Random Forest Evaluation ---")
print(f"Global RF Test MAE: {global_mae:.2f}")

# Compare a few predictions with actual sales
comparison = test[
    ["StockCode", "InvoiceDate", "UnitsSold"]
].copy()

comparison["PredictedSales"] = global_predictions
comparison["AbsoluteError"] = (
    comparison["UnitsSold"] - comparison["PredictedSales"]
).abs()

print("\n--- First 10 Predictions vs Actual ---")
print(comparison.head(10).to_string(index=False))

assert len(global_predictions) == len(y_test)
assert global_mae >= 0


# Compare all models on identical test rows
naive_mae = mean_absolute_error(
    y_test,
    X_test["Lag1"]
)

moving_average_mae = mean_absolute_error(
    y_test,
    X_test["RollingMean3"]
)

print("\n--- Global Forecasting Showdown ---")
print(f"Naive MAE:          {naive_mae:.2f}")
print(f"Moving Average MAE: {moving_average_mae:.2f}")
print(f"Global RF MAE:      {global_mae:.2f}")

scores = {
    "Naive": naive_mae,
    "Moving Average": moving_average_mae,
    "Global Random Forest": global_mae
}

best_model = min(scores, key=scores.get)

print(f"\nBest model: {best_model}")


# Compare forecasting models for each product
comparison["NaiveError"] = (
    comparison["UnitsSold"] - X_test["Lag1"].to_numpy()
).abs()

comparison["MovingAverageError"] = (
    comparison["UnitsSold"] - X_test["RollingMean3"].to_numpy()
).abs()

product_results = (
    comparison.groupby("StockCode")[
        ["NaiveError", "MovingAverageError", "AbsoluteError"]
    ]
    .mean()
)

product_results["BestModel"] = product_results[
    ["NaiveError", "MovingAverageError", "AbsoluteError"]
].idxmin(axis=1)

print("\n--- Best Model Per Product ---")
print(product_results["BestModel"].value_counts())

print("\n--- Average Product MAE ---")
print(
    product_results[
        ["NaiveError", "MovingAverageError", "AbsoluteError"]
    ].mean().round(2)
)


# Identify ties between forecasting models
error_columns = [
    "NaiveError",
    "MovingAverageError",
    "AbsoluteError"
]

minimum_errors = product_results[error_columns].min(axis=1)

is_best = product_results[error_columns].eq(
    minimum_errors,
    axis=0
)

# Count how many models share the lowest MAE
product_results["NumberOfWinners"] = is_best.sum(axis=1)

unique_winners = product_results[
    product_results["NumberOfWinners"] == 1
]

tied_products = product_results[
    product_results["NumberOfWinners"] > 1
]

print("\n--- Forecasting Wins Without Ties ---")
print(unique_winners["BestModel"].value_counts())

print("\nProducts with tied best models:", len(tied_products))

assert len(unique_winners) + len(tied_products) == len(product_results)


# Compare products with and without training examples
training_products = set(train["StockCode"])

comparison["ProductGroup"] = comparison["StockCode"].apply(
    lambda code: (
        "Established"
        if code in training_products
        else "Test-only"
    )
)

group_results = comparison.groupby("ProductGroup").agg(
    Products=("StockCode", "nunique"),
    TestRows=("StockCode", "size"),
    NaiveMAE=("NaiveError", "mean"),
    MovingAverageMAE=("MovingAverageError", "mean"),
    RandomForestMAE=("AbsoluteError", "mean")
)

print("\n--- Established vs Test-only Products ---")
print(group_results.round(2).to_string())

assert group_results["TestRows"].sum() == len(test)
assert group_results["Products"].sum() == test["StockCode"].nunique()


import numpy as np

# Reproduce the model using the same settings
repeat_model = RandomForestRegressor(
    n_estimators=50,
    max_depth=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)

repeat_model.fit(X_train, y_train)

repeat_predictions = repeat_model.predict(X_test)

assert np.allclose(
    global_predictions,
    repeat_predictions,
    rtol=1e-10,
    atol=1e-8
)

print("\n--- Reproducibility Check ---")
print("Repeated predictions match: YES")


from pathlib import Path

# Save product-level evaluation results
output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "global_model_evaluation.csv"

product_results.to_csv(
    output_path,
    index=True,
    index_label="StockCode"
)

print("\n--- Evaluation Export ---")
print("Saved to:", output_path)
print("Products exported:", len(product_results))

assert output_path.exists()
