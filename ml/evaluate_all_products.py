
import pandas as pd

from ml.forecast_baseline import evaluate_product_baselines


# Load the weekly forecasting dataset
weekly = pd.read_csv(
    "data/processed/weekly_sales.csv",
    dtype={"StockCode": str},
    parse_dates=["InvoiceDate"]
)

results = []

# Evaluate each product independently
for stock_code, product_sales in weekly.groupby("StockCode"):

    # Skip products with insufficient history
    if len(product_sales) < 20:
        continue

    scores = evaluate_product_baselines(product_sales)

    results.append({
        "StockCode": stock_code,
        "NaiveMAE": scores["naive_mae"],
        "MovingAverageMAE": scores["moving_average_mae"],
        "TestWeeks": scores["test_weeks"]
    })

# Convert results to a DataFrame
evaluation = pd.DataFrame(results)

print("\n--- DemandLens Multi-Product Evaluation ---")
print("Products evaluated:", len(evaluation))

print(
    "Average Naive MAE:",
    round(evaluation["NaiveMAE"].mean(), 2)
)

print(
    "Average Moving Average MAE:",
    round(evaluation["MovingAverageMAE"].mean(), 2)
)

print(
    "Products where Naive wins:",
    (evaluation["NaiveMAE"] < evaluation["MovingAverageMAE"]).sum()
)

print(
    "Products where Moving Average wins:",
    (evaluation["MovingAverageMAE"] < evaluation["NaiveMAE"]).sum()
)

print(
    "Ties:",
    (evaluation["NaiveMAE"] == evaluation["MovingAverageMAE"]).sum()
)

print("\nEvaluation complete!")


# Save model evaluation results
output_path = "data/processed/baseline_evaluation.csv"

evaluation.to_csv(output_path, index=False)

# Verify the exported results
saved_results = pd.read_csv(
    output_path,
    dtype={"StockCode": str}
)

assert len(saved_results) == len(evaluation)
assert saved_results["StockCode"].nunique() == 4067

assert saved_results[
    ["NaiveMAE", "MovingAverageMAE"]
].notna().all().all()

print("\n--- Evaluation Export ---")
print("Saved to:", output_path)
print("Products:", len(saved_results))
print("Export verification passed!")
