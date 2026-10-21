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
