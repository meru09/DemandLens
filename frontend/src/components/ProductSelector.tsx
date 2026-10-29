
"use client";

import {
  useEffect,
  useId,
  useRef,
  useState,
} from "react";

import type { KeyboardEvent } from "react";

import SalesChart from "@/components/SalesChart";
import ForecastCard from "@/components/ForecastCard";

import type {
  ProductHistoryResponse,
  ForecastResponse,
} from "@/types/api";

type ProductSelectorProps = {
  products: string[];
};

const MAX_RESULTS = 10;

export default function ProductSelector({
  products,
}: ProductSelectorProps) {
  // Search and selection state
  const [selectedProduct, setSelectedProduct] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  // Product data
  const [salesHistory, setSalesHistory] =
    useState<ProductHistoryResponse | null>(null);

  const [forecast, setForecast] =
    useState<ForecastResponse | null>(null);

  // Loading and error states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [forecastError, setForecastError] = useState("");

  // References
  const searchContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listboxId = useId();

  // Filter the full product list
  const normalizedQuery = searchQuery.trim().toLowerCase();

  const matchingProducts = products.filter((product) =>
    product.toLowerCase().includes(normalizedQuery)
  );

  // Only limit the displayed results
  const visibleProducts = matchingProducts.slice(
    0,
    MAX_RESULTS
  );

  // Select product and close dropdown
  function handleProductChange(product: string) {
    setSelectedProduct(product);
    setSearchQuery(product);
    setIsSearchOpen(false);
    setActiveIndex(-1);

    setSalesHistory(null);
    setForecast(null);
    setError("");
    setForecastError("");
    setLoading(true);

    // Remove focus from search input
    inputRef.current?.blur();
  }

  // Update search query
  function handleSearchChange(value: string) {
    setSearchQuery(value);
    setIsSearchOpen(true);
    setActiveIndex(-1);
  }

  // Keyboard navigation
  function handleKeyDown(
    event: KeyboardEvent<HTMLInputElement>
  ) {
    if (event.key === "Escape") {
      setIsSearchOpen(false);
      setActiveIndex(-1);
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setIsSearchOpen(true);

      if (visibleProducts.length > 0) {
        setActiveIndex((current) =>
          current >= visibleProducts.length - 1
            ? 0
            : current + 1
        );
      }

      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setIsSearchOpen(true);

      if (visibleProducts.length > 0) {
        setActiveIndex((current) =>
          current <= 0
            ? visibleProducts.length - 1
            : current - 1
        );
      }

      return;
    }

    if (
      event.key === "Enter" &&
      isSearchOpen &&
      visibleProducts.length > 0
    ) {
      event.preventDefault();

      const index = activeIndex >= 0 ? activeIndex : 0;

      handleProductChange(visibleProducts[index]);
    }
  }

  // Close dropdown on outside interaction
  useEffect(() => {
    function handleOutsideClick(event: PointerEvent) {
      const container = searchContainerRef.current;

      if (
        container &&
        !container.contains(event.target as Node)
      ) {
        setIsSearchOpen(false);
        setActiveIndex(-1);
      }
    }

    document.addEventListener(
      "pointerdown",
      handleOutsideClick,
      true
    );

    return () => {
      document.removeEventListener(
        "pointerdown",
        handleOutsideClick,
        true
      );
    };
  }, []);

  // Fetch history and forecast when product changes
  useEffect(() => {
    if (!selectedProduct) {
      return;
    }

    const controller = new AbortController();

    async function fetchProductData() {
      try {
        // Historical sales
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

        // Forecast
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
    <div className="min-w-0 rounded-xl border border-violet-900/40 bg-[#171728] p-4 sm:p-6">
      {/* Searchable product selector */}
      <div
        ref={searchContainerRef}
        className="relative"
      >
        <label
          htmlFor="product-search"
          className="mb-3 block text-sm font-medium text-slate-300"
        >
          Select a Product
        </label>

        <div className="relative">
          <span
            aria-hidden="true"
            className="pointer-events-none absolute inset-y-0 left-4 flex items-center text-violet-400"
          >
            ⌕
          </span>

          <input
            ref={inputRef}
            id="product-search"
            type="text"
            role="combobox"
            aria-autocomplete="list"
            aria-expanded={isSearchOpen}
            aria-controls={listboxId}
            aria-activedescendant={
              isSearchOpen && activeIndex >= 0
                ? `${listboxId}-option-${activeIndex}`
                : undefined
            }
            value={searchQuery}
            onChange={(event) =>
              handleSearchChange(event.target.value)
            }
            onFocus={() => setIsSearchOpen(true)}
            onKeyDown={handleKeyDown}
            placeholder="Search by product code..."
            autoComplete="off"
            className="w-full rounded-lg border border-violet-800/50 bg-[#0B0B16] py-3 pl-11 pr-4 text-white placeholder:text-slate-500 outline-none focus:border-violet-400 focus-visible:ring-2 focus-visible:ring-violet-400"
          />
        </div>

        {/* Search results */}
        {isSearchOpen && (
          <div className="absolute z-30 mt-2 w-full overflow-hidden rounded-xl border border-violet-800/50 bg-[#10101F] shadow-xl shadow-black/30">
            <div className="border-b border-violet-900/30 px-4 py-3">
              <p
                role="status"
                className="text-xs text-slate-400"
              >
                {matchingProducts.length.toLocaleString()}{" "}
                {matchingProducts.length === 1
                  ? "product"
                  : "products"}{" "}
                found
                {matchingProducts.length > MAX_RESULTS &&
                  ` · Showing first ${MAX_RESULTS}`}
              </p>
            </div>

            {visibleProducts.length > 0 ? (
              <ul
                id={listboxId}
                role="listbox"
                aria-label="Matching products"
                className="max-h-64 overflow-y-auto p-2"
              >
                {visibleProducts.map((product, index) => (
                  <li
                    key={product}
                    id={`${listboxId}-option-${index}`}
                    role="option"
                    aria-selected={
                      product === selectedProduct
                    }
                    className={`cursor-pointer rounded-lg px-4 py-3 text-sm transition-colors ${
                      index === activeIndex
                        ? "bg-violet-600/20 text-violet-200"
                        : "text-slate-200 hover:bg-violet-500/10"
                    }`}
                    onMouseDown={(event) =>
                      event.preventDefault()
                    }
                    onClick={() =>
                      handleProductChange(product)
                    }
                    onMouseEnter={() =>
                      setActiveIndex(index)
                    }
                  >
                    Product {product}
                  </li>
                ))}
              </ul>
            ) : (
              <div
                id={listboxId}
                className="px-4 py-5 text-sm text-slate-400"
              >
                No matching products. Try another code.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Selected product indicator */}
      {selectedProduct && (
        <p className="mt-4 text-xs text-slate-400">
          Selected product:{" "}
          <span className="font-medium text-violet-300">
            {selectedProduct}
          </span>
        </p>
      )}

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

      {/* Compact product summary */}
      {salesHistory && (
        <div className="mt-6 grid grid-cols-2 gap-3 sm:gap-4">
          <div className="min-w-0 rounded-xl border border-violet-800/30 bg-[#0B0B16] p-3 sm:p-5">
            <p className="text-xs font-medium text-slate-400 sm:text-sm">
              Product Code
            </p>

            <p className="mt-3 break-all text-xl font-bold text-violet-300 sm:text-2xl">
              {salesHistory.stock_code}
            </p>
          </div>

          <div className="min-w-0 rounded-xl border border-violet-800/30 bg-[#0B0B16] p-3 sm:p-5">
            <p className="text-xs font-medium text-slate-400 sm:text-sm">
              Historical Weeks
            </p>

            <p className="mt-3 text-xl font-bold text-white sm:text-2xl">
              {salesHistory.total_weeks.toLocaleString()}
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

      {/* Forecast */}
      {forecast && (
        <ForecastCard forecast={forecast} />
      )}

      {/* Forecast unavailable */}
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
