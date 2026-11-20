# DemandLens Dashboard Design Specification

**Status:** Approved and implemented. The user authorized implementation after
review; this document records the delivered dashboard scope and data decisions.

## Decisions captured

- Use real DemandLens data and backend results; do not present screenshot or
  placeholder values as live metrics.
- The primary product forecast is for the next **three weeks**.
- Extend the backend additively. Keep the existing API response contracts
  working for current callers.
- Scope this design to the existing main dashboard (`/`). The other Stitch
  screen designs are future work, not part of this implementation.

## 1. Current application and data

The current frontend is a Next.js app with one dashboard route. The existing
`[page.tsx](../frontend/src/app/page.tsx)` loads the product list, and
`[ProductSelector.tsx](../frontend/src/components/ProductSelector.tsx)` loads
the selected product's weekly history and forecast. The page currently contains
a hard-coded total-units value; replace it with an API-sourced value before
showing it as a metric.

The current backend contracts are:

| Endpoint | Current behavior |
| --- | --- |
| `GET /products` | Returns the product count and the first 10 product codes. |
| `GET /products/{stock_code}/history` | Returns weekly historical units for one product. |
| `GET /products/{stock_code}/forecast` | Returns one forecast week, its date, predicted units, and model name. |

These are implemented in `[backend/main.py](../backend/main.py)`;
`[ForecastResponse](../backend/schemas.py)` describes the existing one-week
response. The current model in `[forecast_service.py](../backend/forecast_service.py)`
uses the previous three observed weeks to predict **one** week. Therefore,
`moving_average_3` describes a three-week look-back window, not a three-week
forecast horizon.

Available data includes:

- `[weekly_sales.csv](../data/processed/weekly_sales.csv)`: `InvoiceDate`,
  `StockCode`, and `UnitsSold`.
- `[baseline_evaluation.csv](../data/processed/baseline_evaluation.csv)`:
  per-product naive and moving-average MAE plus test-week counts. These metrics
  are not three-week-horizon metrics and the file does not currently include
  RMSE.
- `[cleaned_sales.csv](../data/processed/cleaned_sales.csv)`: cleaned invoice,
  product, quantity, date, and price fields. The cleaning pipeline excludes
  cancellation invoices and records with nonpositive quantity or price.

The Emerald palette and three fonts are already defined in
`[globals.css](../frontend/src/app/globals.css)` and
`[layout.tsx](../frontend/src/app/layout.tsx)`. Several components still use
hard-coded violet styles, so the visual system is only partially applied.
`[Sidebar.tsx](../frontend/src/components/Sidebar.tsx)` currently has only the
Dashboard route; do not add active links to screens that do not exist.

## 2. Design direction

Use the existing Emerald Intelligence tokens consistently:

- Canvas: `#081612`; sidebar: `#04110d`.
- Cards: `#101e1a`; nested surfaces: `#14221e` and `#1f2d28`.
- Historical actuals and primary actions: emerald `#4edea3`.
- Forecast line and forecast-only highlights: lime `#98da27`.
- Negative values: coral `#ffb4ab`.
- Main, secondary, and muted text: `#d6e6df`, `#bbcabf`, `#86948a`.

Use the already loaded Inter, Space Grotesk, and JetBrains Mono fonts. Replace
component-level violet and raw surface colors with the existing CSS/Tailwind
tokens. Preserve keyboard focus visibility, the accessible mobile sidebar
drawer, and the product selector's keyboard-operable combobox.

## 3. Main dashboard layout

Keep the dashboard as the only in-scope page:

1. **Responsive app shell:** Emerald sidebar and a top header with the page
   title and brief historical-data context. Do not present unimplemented
   navigation routes as working pages.
2. **KPI row:** Show only metrics backed by an API response:
   - Total units sold across the available weekly dataset.
   - Product count.
   - Transaction count, based on distinct invoice IDs in cleaned sales data.
   - Average units per week, calculated as total units divided by distinct
     observed weeks in the weekly dataset.
   - No KPI period deltas; the dashboard lacks a matched reporting-period
     definition. The separate demand trend compares the latest 12 observed
     weeks with the preceding 12.
3. **Analytics workspace:** Responsive 8:4 layout:
   - Left: selected-product history and a three-week forecast chart, followed
     by model-evaluation and trend details when their data is available.
   - Right: searchable product selection and a three-row forecast summary for
     weeks 1–3 ahead.
4. **States:** Update loading, empty, API-error, and forecast-unavailable
   displays to use the Emerald theme. If history loads but the forecast fails,
   keep history visible and explain that the forecast is unavailable.

The historical chart-range selector, if retained (`4W`, `12W`, `26W`, `1Y`),
controls **how much past history is displayed**. It does not change the fixed
three-week forecast horizon.

### Three-week forecast visualization

- Historical actuals use a solid emerald line.
- Predictions use a dashed lime line beginning after the last observed week,
  with a visible actual/forecast boundary.
- Show exactly three future weekly dates and their predicted units.
- Identify the model and forecast origin so the user can see that this is a
  forecast relative to the dataset's latest observation, not a live prediction
  for today's date.
- Keep the API's raw numeric predictions; format them consistently in the UI.
  Do not invent confidence percentages or confidence bands.

## 4. Backward-compatible API additions

Do not change or remove the current `/products`, `/history`, or one-week
`/forecast` response shapes. Keep their existing tests passing. Add separately
typed API responses and new routes for the new dashboard needs.

### A. Three-week forecast

Add a route such as:

```text
GET /products/{stock_code}/forecasts?horizon=3
```

Return the product code, model, latest observed date, horizon, and three
`{forecast_date, predicted_units}` points. Generate dates one week apart after
the latest actual observation. The initial candidate is recursive MA(3): use
the last three actual values for week 1, then append each prediction to the
series before calculating the next step. Name and document this method explicitly, and show its per-product
three-week-horizon backtest beside the forecast. Keep the existing one-week
route's output unchanged. The new route accepts horizons 1–3; the dashboard
requests 3.

Validate the horizon and product, and preserve the current 404/422 error
behavior patterns. The exact allowed horizon range should be fixed in the API
contract before implementation; the dashboard itself requests three weeks.

### B. Forecast evaluation

Extend the offline evaluation pipeline to backtest at forecast leads 1, 2, and
3. Report MAE and RMSE per horizon, with the number of evaluation origins and
the evaluation method. Do not reuse the existing one-step MAE as evidence for
three-week accuracy. Expose the resulting metrics through a new product
evaluation endpoint or a clearly defined additive dashboard API.

Only display RMSE after it has been calculated from the actual backtest
predictions. The current evaluation CSV contains MAE but not RMSE.

### C. Dashboard summary and product search

Add a dashboard summary response for real aggregate KPIs. Define each metric
before showing it:

- Units sold: sum `UnitsSold` over the reported period.
- Product count: distinct valid product codes in the dataset.
- Transactions: distinct invoice IDs from cleaned sales data.
- Average weekly demand: total units divided by distinct observed weeks.
- Period deltas: omitted until a reporting period is defined.

Do not label `Quantity * Price` as currency revenue until the dataset's
currency and aggregation rules are confirmed. If shown later, define treatment
of returns and cancellations.

The existing `/products` endpoint returns only the first 10 codes. Add an
optional search/pagination contract or a separate product-search endpoint so
the selector can search the full catalog. Preserve the existing no-query
behavior and response for current consumers.

## 5. Unsupported or deferred claims

- The current source does not contain inventory-on-hand or lead-time data.
  Defer the “increase inventory” recommendation until those inputs and a
  recommendation rule exist.
- The current forecast and evaluation data do not provide calibrated
  prediction intervals. Do not display a confidence percentage or shaded
  confidence band until the interval method is calibrated and tested at the
  three forecast leads.
- Avoid unsupported sales-growth percentages, model-performance values, and
  transaction or revenue figures. Loading, unavailable, or omitted states are
  preferable to sample values presented as real.

## 6. Implementation and verification

- The existing `/products`, `/history`, and one-week `/forecast` contracts
  remain available. Additive APIs provide full-catalog product search, the
  dashboard summary, forecasts for horizons 1–3, and per-horizon evaluation.
- The dashboard uses real weekly history and recursively forecasts the next
  three weeks with MA(3). Evaluation reports rolling-origin MAE/RMSE by lead;
  the UI displays three-week metrics and compares MAE with a last-value
  baseline. The forecast remains an initial model, not a guarantee of
  superiority for every product.
- The dashboard reports all-time dataset aggregates; it does not display
  currency revenue, confidence intervals, or inventory recommendations.
- Backend tests, frontend lint, and production build pass. Runtime checks
  confirmed the dashboard summary and new APIs return successfully. Browser
  validation confirmed product selection renders history, exactly three future
  forecast rows, and evaluation metrics at mobile and desktop widths.

## 7. Decisions and deferred items

- Dashboard-only scope; other screen designs remain future work.
- The forecast horizon is fixed at three weeks in the dashboard.
- Transactions are distinct cleaned invoice IDs. Currency revenue is omitted
  until currency and aggregation rules are confirmed.
- Period-change cards remain omitted until reporting windows are defined.
- Confidence UI and inventory recommendations remain deferred until backed by
  calibrated forecast intervals and inventory/lead-time data, respectively.
