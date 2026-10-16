
import pandas as pd

from ml.feature_engineering import create_lag_features
from ml.forecast_baseline import chronological_split, calculate_mae
from sklearn.ensemble import RandomForestRegressor
from ml.forecast_baseline import (create_naive_predictions, create_moving_average_predictions)



# Load our weekly sales dataset
weekly = pd.read_csv(
    "data/processed/weekly_sales.csv",
    dtype={"StockCode": str},
    parse_dates=["InvoiceDate"]
)

# Start with one product
product_sales = weekly[
    weekly["StockCode"] == "10002"
].copy()

# Create machine learning features
features = create_lag_features(product_sales)

# Separate inputs (X) and target (y)
feature_columns = [
    "Lag1",
    "Lag2",
    "Lag3",
    "RollingMean3"
]

X = features[feature_columns]
y = features["UnitsSold"]

print("\n--- DemandLens ML Features ---")
print("Product:", "10002")
print("Original weeks:", len(product_sales))
print("Training examples:", len(features))

print("\nFeature matrix (X):")
print(X.head())

print("\nTarget values (y):")
print(y.head())

print("\nFeature shape:", X.shape)
print("Target shape:", y.shape)


# Split feature rows chronologically
train, test = chronological_split(
    features,
    train_ratio=0.8
)

print("\n--- ML Train/Test Split ---")
print("Training examples:", len(train))
print("Testing examples:", len(test))

print("Last training date:", train["InvoiceDate"].max())
print("First testing date:", test["InvoiceDate"].min())

# Verify chronological separation
assert train["InvoiceDate"].max() < test["InvoiceDate"].min()

print("Chronological split verified!")


# Prepare training inputs and targets
feature_columns = [
    "Lag1",
    "Lag2",
    "Lag3",
    "RollingMean3"
]

X_train = train[feature_columns]
y_train = train["UnitsSold"]

# Create our first ML model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

# Train using historical data only
model.fit(X_train, y_train)

print("\n--- Random Forest Training ---")
print("Training examples:", len(X_train))
print("Features:", list(X_train.columns))
print("Number of trees:", model.n_estimators)
print("Model training complete!")


# Prepare unseen test examples
X_test = test[feature_columns]
y_test = test["UnitsSold"]

# Generate predictions
predictions = model.predict(X_test)

# Compare predictions with actual sales
comparison = pd.DataFrame({
    "InvoiceDate": test["InvoiceDate"].to_numpy(),
    "ActualSales": y_test.to_numpy(),
    "PredictedSales": predictions
})

print("\n--- Random Forest Predictions ---")
print(comparison.head())

print("\nTotal test predictions:", len(predictions))
print("Minimum prediction:", round(predictions.min(), 2))
print("Maximum prediction:", round(predictions.max(), 2))


# Evaluate Random Forest predictions
rf_mae = calculate_mae(
    y_test,
    predictions
)

print("\n--- Random Forest Evaluation ---")
print("Product:", "10002")
print("Test weeks:", len(y_test))
print("Random Forest MAE:", round(rf_mae, 2))

# Basic prediction checks
assert len(predictions) == len(y_test)
assert pd.notna(predictions).all()

print("Prediction verification passed!")


# Compare all models on identical test weeks
baseline_data = pd.concat(
    [train.tail(3), test],
    ignore_index=True
)

naive = create_naive_predictions(baseline_data)

moving = create_moving_average_predictions(
    baseline_data,
    window=3
)

test_dates = set(test["InvoiceDate"])

naive = naive[
    naive["InvoiceDate"].isin(test_dates)
].sort_values("InvoiceDate")

moving = moving[
    moving["InvoiceDate"].isin(test_dates)
].sort_values("InvoiceDate")

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

print("\n--- Fair Model Comparison ---")
print("Test weeks:", len(test))
print("Naive MAE:", round(naive_mae, 2))
print("Moving Average MAE:", round(moving_mae, 2))
print("Random Forest MAE:", round(rf_mae, 2))


# Diagnose model performance on training vs test data
train_predictions = model.predict(X_train)

train_mae = calculate_mae(
    y_train,
    train_predictions
)

print("\n--- Random Forest Diagnostics ---")
print("Training MAE:", round(train_mae, 2))
print("Testing MAE:", round(rf_mae, 2))
print("Error gap:", round(rf_mae - train_mae, 2))


# Experiment: a less complex Random Forest
simple_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=3,
    min_samples_leaf=5,
    random_state=42
)

simple_model.fit(X_train, y_train)

# Evaluate training and test performance
simple_train_predictions = simple_model.predict(X_train)
simple_test_predictions = simple_model.predict(X_test)

simple_train_mae = calculate_mae(
    y_train,
    simple_train_predictions
)

simple_test_mae = calculate_mae(
    y_test,
    simple_test_predictions
)

print("\n--- Simplified Random Forest ---")
print("Training MAE:", round(simple_train_mae, 2))
print("Testing MAE:", round(simple_test_mae, 2))
print("Original RF Test MAE:", round(rf_mae, 2))
print("Moving Average MAE:", round(moving_mae, 2))


# Inspect feature importance
importance = pd.DataFrame({
    "Feature": feature_columns,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    "Importance",
    ascending=False
)

print("\n--- Random Forest Feature Importance ---")
print(importance.to_string(index=False))

# Verify feature importances
assert len(importance) == 4
assert abs(importance["Importance"].sum() - 1.0) < 1e-6
