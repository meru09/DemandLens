export type WeeklySale = {
  InvoiceDate: string;
  UnitsSold: number;
};

export type ProductHistoryResponse = {
  stock_code: string;
  total_weeks: number;
  history: WeeklySale[];
};

export type ForecastResponse = {
  stock_code: string;
  forecast_date: string;
  predicted_units: number;
  model: string;
};

export type ForecastPoint = {
  forecast_date: string;
  predicted_units: number;
};

export type ForecastHorizonResponse = {
  stock_code: string;
  forecast_origin: string;
  model: string;
  horizon_weeks: number;
  forecasts: ForecastPoint[];
};

export type ForecastHorizonMetric = {
  horizon_weeks: number;
  evaluation_origins: number;
  naive_mae: number | null;
  naive_rmse: number | null;
  moving_average_mae: number | null;
  moving_average_rmse: number | null;
};

export type ProductForecastEvaluationResponse = {
  stock_code: string;
  evaluation_method: string;
  metrics: ForecastHorizonMetric[];
};

export type ProductSearchResponse = {
  query: string;
  total_matches: number;
  products: string[];
};

export type DashboardSummaryResponse = {
  dataset_start: string;
  dataset_end: string;
  weeks: number;
  total_units_sold: number;
  total_products: number;
  total_transactions: number;
  average_units_per_week: number;
};

export type ProductsResponse = {
  total_products: number;
  products: string[];
};
