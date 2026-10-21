"use client";

import { useEffect, useState } from "react";
import SalesChart from "@/components/SalesChart";
import ForecastCard from "@/components/ForecastCard";


import type {
  ProductHistoryResponse,
  ForecastResponse,
} from "@/types/api";

type ProductSelectorProps = {
  products: string[];
};

export default function ProductSelector({
  products,
}: ProductSelectorProps) {
  const [selectedProduct, setSelectedProduct] = useState("");

  const [salesHistory, setSalesHistory] =
    useState<ProductHistoryResponse | null>(null);

  const [forecast, setForecast] =
    useState<ForecastResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!selectedProduct) {
      setSalesHistory(null);
      setForecast(null);
      return;
    }

    const controller = new AbortController();

    async function fetchProductData() {
      setLoading(true);
      setError("");
      setSalesHistory(null);
      setForecast(null);

      try {
        // Fetch historical weekly sales
        const historyResponse = await fetch(
          `http://127.0.0.1:8000/products/${encodeURIComponent(selectedProduct)}/history`,
          { signal: controller.signal }
        );

        if (!historyResponse.ok) {
          throw new Error("Failed to fetch product history");
        }

        const historyData: ProductHistoryResponse =
          await historyResponse.json();

        if (!controller.signal.aborted) {
          setSalesHistory(historyData);
        }

        // Fetch next-week forecast
        const forecastResponse = await fetch(
          `http://127.0.0.1:8000/products/${encodeURIComponent(selectedProduct)}/forecast`,
          { signal: controller.signal }
        );

        if (!forecastResponse.ok) {
          throw new Error("Failed to fetch product forecast");
        }

        const forecastData: ForecastResponse =
          await forecastResponse.json();

        if (!controller.signal.aborted) {
          setForecast(forecastData);
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load product data."
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    fetchProductData();

    return () => controller.abort();
  }, [selectedProduct]);

  return (
    <div className="rounded-xl border border-violet-900/40 bg-[#171728] p-6">
      {/* Product selector */}
      <label
        htmlFor="product-select"
        className="mb-3 block text-sm font-medium text-slate-300"
      >
        Select a Product
      </label>

      <select
        id="product-select"
        value={selectedProduct}
        onChange={(event) =>
          setSelectedProduct(event.target.value)
        }
        className="w-full rounded-lg border border-violet-800/50 bg-[#0B0B16] px-4 py-3 text-white outline-none focus:border-violet-400"
      >
        <option value="" disabled>
          Choose a product...
        </option>

        {products.map((product) => (
          <option key={product} value={product}>
            Product {product}
          </option>
        ))}
      </select>

      {/* Loading state */}
      {loading && (
        <p className="mt-4 text-sm text-violet-300">
          Loading product data...
        </p>
      )}

      {/* Error state */}
      {error && (
        <p role="alert" className="mt-4 text-sm text-red-400">
          {error}
        </p>
      )}

      {/* Historical sales information */}
      {salesHistory && (
        <div className="mt-6 rounded-lg border border-violet-800/30 bg-[#0B0B16] p-4">
          <p className="text-sm text-slate-400">
            Selected Product
          </p>

          <p className="mt-2 text-xl font-semibold text-violet-300">
            {salesHistory.stock_code}
          </p>

          <div className="mt-3 flex items-center justify-between">
            <p className="text-sm text-slate-400">
              Historical Weeks
            </p>

            <p className="text-lg font-semibold text-white">
              {salesHistory.total_weeks}
            </p>
          </div>
        </div>
      )}

      {/* Historical sales chart */}
      {salesHistory && (
        <SalesChart data={salesHistory.history} />
      )}

      {/* Next Week Forecast */}
      {forecast && (
        <ForecastCard forecast={forecast} />
  )}
    </div>
  );
}
