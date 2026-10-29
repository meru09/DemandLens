
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
  const [forecastError, setForecastError] = useState("");

  // Handle product selection and reset previous data
  function handleProductChange(product: string) {
    setSelectedProduct(product);
    setSalesHistory(null);
    setForecast(null);
    setError("");
    setForecastError("");
    setLoading(Boolean(product));
  }

  useEffect(() => {
    if (!selectedProduct) {
      return;
    }

    const controller = new AbortController();

    async function fetchProductData() {
      try {
        // Fetch historical weekly sales
        const historyResponse = await fetch(
          `http://127.0.0.1:8000/products/${encodeURIComponent(
            selectedProduct
          )}/history`,
          { signal: controller.signal }
        );

        if (!historyResponse.ok) {
          throw new Error(
            "Failed to fetch product history."
          );
        }

        const historyData: ProductHistoryResponse =
          await historyResponse.json();

        // Validate history response
        if (
          !historyData ||
          !Array.isArray(historyData.history) ||
          typeof historyData.total_weeks !== "number" ||
          !Number.isFinite(historyData.total_weeks) ||
          historyData.total_weeks < 0 ||
          typeof historyData.stock_code !== "string" ||
          historyData.stock_code !== selectedProduct
        ) {
          throw new Error(
            "Invalid sales history data received."
          );
        }

        if (controller.signal.aborted) {
          return;
        }

        setSalesHistory(historyData);

        // Fetch forecast independently
        try {
          const forecastResponse = await fetch(
            `http://127.0.0.1:8000/products/${encodeURIComponent(
              selectedProduct
            )}/forecast`,
            { signal: controller.signal }
          );

          if (!forecastResponse.ok) {
            throw new Error(
              "Forecast unavailable for this product."
            );
          }

          const forecastData: ForecastResponse =
            await forecastResponse.json();

          // Validate forecast response
          if (
            !forecastData ||
            typeof forecastData.stock_code !== "string" ||
            forecastData.stock_code !== selectedProduct ||
            typeof forecastData.predicted_units !== "number" ||
            !Number.isFinite(forecastData.predicted_units) ||
            forecastData.predicted_units < 0 ||
            typeof forecastData.forecast_date !== "string" ||
            !/^\d{4}-\d{2}-\d{2}$/.test(
              forecastData.forecast_date
            ) ||
            Number.isNaN(
              Date.parse(
                `${forecastData.forecast_date}T00:00:00Z`
              )
            ) ||
            typeof forecastData.model !== "string" ||
            !forecastData.model.trim()
          ) {
            throw new Error(
              "Invalid forecast data received."
            );
          }

          if (!controller.signal.aborted) {
            setForecast(forecastData);
          }
        } catch (forecastErr) {
          if (!controller.signal.aborted) {
            setForecastError(
              forecastErr instanceof Error
                ? forecastErr.message
                : "Unable to retrieve forecast."
            );
          }
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
          handleProductChange(event.target.value)
        }
        className="w-full rounded-lg border border-violet-800/50 bg-[#0B0B16] px-4 py-3 text-white outline-none focus:border-violet-400 focus-visible:ring-2 focus-visible:ring-violet-400"
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
        <p
          role="status"
          className="mt-4 text-sm text-violet-300"
        >
          Loading product data...
        </p>
      )}

      {/* Sales history error */}
      {error && (
        <div
          role="alert"
          className="mt-4 rounded-lg border border-red-800/40 bg-red-950/20 p-4"
        >
          <p className="font-medium text-red-300">
            Unable to load sales history
          </p>

          <p className="mt-2 text-sm text-red-400">
            {error}
          </p>
        </div>
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

      {/* Historical sales chart or empty state */}
      {salesHistory &&
        (salesHistory.history.length > 0 ? (
          <SalesChart data={salesHistory.history} />
        ) : (
          <div
            role="status"
            className="mt-6 rounded-lg border border-violet-800/30 bg-[#0B0B16] p-6 text-center"
          >
            <p className="font-medium text-slate-200">
              No sales history available
            </p>

            <p className="mt-2 text-sm text-slate-400">
              This product does not have historical
              sales records available for visualization.
            </p>
          </div>
        ))}

      {/* Next-week forecast */}
      {forecast && (
        <ForecastCard forecast={forecast} />
      )}

      {/* Forecast unavailable state */}
      {forecastError && (
        <div
          role="alert"
          className="mt-6 rounded-lg border border-amber-800/40 bg-amber-950/20 p-5"
        >
          <p className="font-medium text-amber-300">
            Forecast unavailable
          </p>

          <p className="mt-2 text-sm text-slate-400">
            {forecastError}
          </p>

          <p className="mt-2 text-xs text-slate-500">
            Historical sales data is still available above.
          </p>
        </div>
      )}
    </div>
  );
}
