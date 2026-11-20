"use client";

import {
  useEffect,
  useId,
  useRef,
  useState,
} from "react";

import type { KeyboardEvent } from "react";

import ForecastCard from "@/components/ForecastCard";
import InsightCards from "@/components/InsightCards";
import SalesChart from "@/components/SalesChart";
import { fetchApiJson } from "@/lib/api";

import type {
  ForecastHorizonResponse,
  ProductForecastEvaluationResponse,
  ProductHistoryResponse,
  ProductSearchResponse,
} from "@/types/api";

type ProductSelectorProps = {
  products: string[];
  totalProducts: number;
};

const MAX_RESULTS = 10;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isValidDate(value: unknown): value is string {
  return (
    typeof value === "string" &&
    /^\d{4}-\d{2}-\d{2}$/.test(value) &&
    !Number.isNaN(Date.parse(`${value}T00:00:00Z`))
  );
}

function isHistoryResponse(
  value: unknown,
  stockCode: string
): value is ProductHistoryResponse {
  if (!isRecord(value) || !Array.isArray(value.history)) {
    return false;
  }

  return (
    value.stock_code === stockCode &&
    typeof value.total_weeks === "number" &&
    Number.isFinite(value.total_weeks) &&
    value.total_weeks === value.history.length &&
    value.history.every(
      (week) =>
        isRecord(week) &&
        isValidDate(week.InvoiceDate) &&
        typeof week.UnitsSold === "number" &&
        Number.isFinite(week.UnitsSold)
    )
  );
}

function isForecastResponse(
  value: unknown,
  stockCode: string,
  forecastOrigin: string
): value is ForecastHorizonResponse {
  if (!isRecord(value) || !Array.isArray(value.forecasts)) {
    return false;
  }

  if (
    value.stock_code !== stockCode ||
    value.forecast_origin !== forecastOrigin ||
    value.horizon_weeks !== 3 ||
    typeof value.model !== "string" ||
    value.forecasts.length !== 3
  ) {
    return false;
  }

  const expectedDate = new Date(`${forecastOrigin}T00:00:00Z`);
  return value.forecasts.every((point) => {
    expectedDate.setUTCDate(expectedDate.getUTCDate() + 7);
    return (
      isRecord(point) &&
      isValidDate(point.forecast_date) &&
      point.forecast_date === expectedDate.toISOString().slice(0, 10) &&
      typeof point.predicted_units === "number" &&
      Number.isFinite(point.predicted_units) &&
      point.predicted_units >= 0
    );
  });
}

function isEvaluationResponse(
  value: unknown,
  stockCode: string
): value is ProductForecastEvaluationResponse {
  if (!isRecord(value) || !Array.isArray(value.metrics)) {
    return false;
  }

  return (
    value.stock_code === stockCode &&
    typeof value.evaluation_method === "string" &&
    value.metrics.every(
      (metric) =>
        isRecord(metric) &&
        typeof metric.horizon_weeks === "number" &&
        typeof metric.evaluation_origins === "number"
    )
  );
}

function errorMessage(error: unknown, fallback: string) {
  return error instanceof Error ? error.message : fallback;
}

export default function ProductSelector({
  products,
  totalProducts,
}: ProductSelectorProps) {
  const [selectedProduct, setSelectedProduct] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [searchResult, setSearchResult] =
    useState<ProductSearchResponse | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState("");

  const [salesHistory, setSalesHistory] =
    useState<ProductHistoryResponse | null>(null);
  const [forecast, setForecast] =
    useState<ForecastHorizonResponse | null>(null);
  const [evaluation, setEvaluation] =
    useState<ProductForecastEvaluationResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");
  const [forecastError, setForecastError] = useState("");
  const [evaluationError, setEvaluationError] = useState("");

  const searchContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listboxId = useId();
  const normalizedQuery = searchQuery.trim();

  const visibleProducts = normalizedQuery
    ? searchResult?.products ?? []
    : products.slice(0, MAX_RESULTS);
  const resultCount = normalizedQuery
    ? searchResult?.total_matches ?? 0
    : totalProducts;

  useEffect(() => {
    if (!isSearchOpen || !normalizedQuery) {
      return;
    }

    const controller = new AbortController();

    const timeoutId = window.setTimeout(async () => {
      if (controller.signal.aborted) {
        return;
      }

      setSearchLoading(true);
      try {
        const result = await fetchApiJson<ProductSearchResponse>(
          `/products/search?q=${encodeURIComponent(normalizedQuery)}&limit=${MAX_RESULTS}`,
          { signal: controller.signal }
        );

        if (
          !Array.isArray(result.products) ||
          typeof result.total_matches !== "number" ||
          result.query !== normalizedQuery
        ) {
          throw new Error("Invalid product search data received.");
        }

        if (!controller.signal.aborted) {
          setSearchResult(result);
        }
      } catch (error) {
        if (!controller.signal.aborted) {
          setSearchError(
            errorMessage(error, "Unable to search products.")
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setSearchLoading(false);
        }
      }
    }, 200);

    return () => {
      window.clearTimeout(timeoutId);
      controller.abort();
    };
  }, [isSearchOpen, normalizedQuery]);

  useEffect(() => {
    function handleOutsideClick(event: PointerEvent) {
      const container = searchContainerRef.current;
      if (container && !container.contains(event.target as Node)) {
        setIsSearchOpen(false);
        setActiveIndex(-1);
      }
    }

    document.addEventListener("pointerdown", handleOutsideClick, true);
    return () => {
      document.removeEventListener(
        "pointerdown",
        handleOutsideClick,
        true
      );
    };
  }, []);

  useEffect(() => {
    if (!selectedProduct) {
      return;
    }

    const controller = new AbortController();

    async function fetchSelectedProduct() {
      setLoading(true);
      setHistoryError("");
      setForecastError("");
      setEvaluationError("");
      setSalesHistory(null);
      setForecast(null);
      setEvaluation(null);

      try {
        const encodedProduct = encodeURIComponent(selectedProduct);
        const history = await fetchApiJson<unknown>(
          `/products/${encodedProduct}/history`,
          { signal: controller.signal }
        );

        if (!isHistoryResponse(history, selectedProduct)) {
          throw new Error("Invalid sales history data received.");
        }

        if (controller.signal.aborted) {
          return;
        }
        setSalesHistory(history);

        const [forecastResult, evaluationResult] =
          await Promise.allSettled([
            fetchApiJson<unknown>(
              `/products/${encodedProduct}/forecasts?horizon=3`,
              { signal: controller.signal }
            ),
            fetchApiJson<unknown>(
              `/products/${encodedProduct}/evaluation`,
              { signal: controller.signal }
            ),
          ]);

        if (controller.signal.aborted) {
          return;
        }

        if (forecastResult.status === "fulfilled") {
          if (
            isForecastResponse(
              forecastResult.value,
              selectedProduct,
              history.history.at(-1)?.InvoiceDate ?? ""
            )
          ) {
            setForecast(forecastResult.value);
          } else {
            setForecastError(
              "Invalid three-week forecast data received."
            );
          }
        } else {
          setForecastError(
            errorMessage(
              forecastResult.reason,
              "Unable to retrieve the three-week forecast."
            )
          );
        }

        if (evaluationResult.status === "fulfilled") {
          if (
            isEvaluationResponse(
              evaluationResult.value,
              selectedProduct
            )
          ) {
            setEvaluation(evaluationResult.value);
          } else {
            setEvaluationError(
              "Invalid forecast evaluation data received."
            );
          }
        } else {
          setEvaluationError(
            errorMessage(
              evaluationResult.reason,
              "Unable to retrieve forecast evaluation."
            )
          );
        }
      } catch (error) {
        if (!controller.signal.aborted) {
          setHistoryError(
            errorMessage(error, "Unable to load product history.")
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void fetchSelectedProduct();
    return () => controller.abort();
  }, [selectedProduct]);

  function handleProductChange(product: string) {
    setSelectedProduct(product);
    setSearchQuery(product);
    setSearchResult(null);
    setSearchLoading(false);
    setSearchError("");
    setIsSearchOpen(false);
    setActiveIndex(-1);
    setLoading(true);
    setSalesHistory(null);
    setForecast(null);
    setEvaluation(null);
    setHistoryError("");
    setForecastError("");
    setEvaluationError("");
    inputRef.current?.blur();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
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
          current >= visibleProducts.length - 1 ? 0 : current + 1
        );
      }
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setIsSearchOpen(true);
      if (visibleProducts.length > 0) {
        setActiveIndex((current) =>
          current <= 0 ? visibleProducts.length - 1 : current - 1
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
      handleProductChange(
        visibleProducts[activeIndex >= 0 ? activeIndex : 0]
      );
    }
  }

  return (
    <div className="grid min-w-0 gap-5 lg:grid-cols-12">
      <section
        aria-label="Selected product analytics"
        className="min-w-0 space-y-5 lg:col-span-8"
      >
        {!selectedProduct && (
          <div className="flex min-h-56 flex-col items-center justify-center rounded-2xl border border-dashed border-border bg-surface-card px-6 text-center">
            <p className="font-display text-lg font-semibold text-foreground">
              Choose a product to explore its demand
            </p>
            <p className="mt-2 max-w-md text-sm leading-relaxed text-text-secondary">
              Search the historical catalog to view observed weekly sales,
              three-week forecasts, and backtested accuracy.
            </p>
          </div>
        )}

        {loading && (
          <p
            role="status"
            className="rounded-xl border border-border bg-surface-card p-4 text-sm text-primary"
          >
            Loading product history and forecast…
          </p>
        )}

        {historyError && (
          <div
            role="alert"
            className="rounded-xl border border-danger/40 bg-danger/10 p-4"
          >
            <p className="font-medium text-danger">
              Unable to load product history
            </p>
            <p className="mt-1 text-sm text-text-secondary">
              {historyError}
            </p>
          </div>
        )}

        {salesHistory && (
          <>
            <div className="grid gap-3 sm:grid-cols-2">
              <article className="rounded-xl border border-border/70 bg-surface-card p-4">
                <p className="text-xs text-text-muted">Selected product</p>
                <p className="mt-2 font-mono text-lg font-semibold text-primary">
                  {salesHistory.stock_code}
                </p>
              </article>
              <article className="rounded-xl border border-border/70 bg-surface-card p-4">
                <p className="text-xs text-text-muted">
                  Observed weeks available
                </p>
                <p className="mt-2 font-display text-2xl font-semibold text-foreground">
                  {salesHistory.total_weeks.toLocaleString("en-US")}
                </p>
              </article>
            </div>

            {salesHistory.history.length > 0 ? (
              <SalesChart
                data={salesHistory.history}
                forecast={forecast}
              />
            ) : (
              <div
                role="status"
                className="rounded-xl border border-border bg-surface-card p-6 text-center"
              >
                <p className="font-medium text-foreground">
                  No sales history available
                </p>
                <p className="mt-2 text-sm text-text-secondary">
                  This product has no historical weekly sales to chart.
                </p>
              </div>
            )}

            {forecastError && (
              <div
                role="alert"
                className="rounded-xl border border-danger/40 bg-danger/10 p-4"
              >
                <p className="font-medium text-danger">
                  Forecast unavailable
                </p>
                <p className="mt-1 text-sm text-text-secondary">
                  {forecastError}
                </p>
                <p className="mt-2 text-xs text-text-muted">
                  Historical sales remain available above.
                </p>
              </div>
            )}

            <InsightCards
              history={salesHistory}
              evaluation={evaluation}
              evaluationError={evaluationError}
            />
          </>
        )}
      </section>

      <aside className="min-w-0 space-y-5 lg:col-span-4">
        <section className="rounded-2xl border border-border/70 bg-surface-card p-5">
          <div>
            <h2 className="font-display text-lg font-semibold text-foreground">
              Product selection
            </h2>
            <p className="mt-1 text-xs text-text-muted">
              Search the full historical catalog.
            </p>
          </div>

          <div
            ref={searchContainerRef}
            className="relative mt-5"
          >
            <label
              htmlFor="product-search"
              className="mb-2 block text-xs font-medium text-text-secondary"
            >
              Product code
            </label>
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
              onChange={(event) => {
                const value = event.target.value;
                setSearchQuery(value);
                setSearchResult(null);
                setSearchLoading(Boolean(value.trim()));
                setSearchError("");
                setIsSearchOpen(true);
                setActiveIndex(-1);
              }}
              onFocus={() => {
                setIsSearchOpen(true);
                if (normalizedQuery) {
                  setSearchLoading(true);
                  setSearchResult(null);
                  setSearchError("");
                }
              }}
              onKeyDown={handleKeyDown}
              placeholder="Search by code…"
              autoComplete="off"
              className="w-full rounded-xl border border-border bg-surface-raised px-4 py-3 text-sm text-foreground placeholder:text-text-muted focus:border-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
            />

            {isSearchOpen && (
              <div
                id={listboxId}
                className="absolute z-30 mt-2 w-full overflow-hidden rounded-xl border border-border bg-surface-elevated shadow-2xl"
              >
                <div className="border-b border-border px-3 py-2.5 text-xs text-text-muted">
                  {normalizedQuery
                    ? searchLoading
                      ? "Searching catalog…"
                      : `${resultCount.toLocaleString("en-US")} matching products`
                    : `Showing ${Math.min(products.length, MAX_RESULTS)} of ${totalProducts.toLocaleString("en-US")} products — type to search`}
                </div>

                {searchError && (
                  <p role="alert" className="px-3 py-3 text-xs text-danger">
                    {searchError}
                  </p>
                )}

                {!searchLoading &&
                  !searchError &&
                  visibleProducts.length > 0 && (
                    <ul
                      role="listbox"
                      aria-label="Matching products"
                      className="max-h-64 overflow-y-auto p-2"
                    >
                      {visibleProducts.map((product, index) => (
                        <li
                          key={product}
                          id={`${listboxId}-option-${index}`}
                          role="option"
                          aria-selected={product === selectedProduct}
                          className={`cursor-pointer rounded-lg px-3 py-2.5 text-sm transition-colors ${
                            index === activeIndex
                              ? "bg-surface-active text-primary"
                              : "text-text-secondary hover:bg-surface-raised hover:text-foreground"
                          }`}
                          onMouseDown={(event) =>
                            event.preventDefault()
                          }
                          onClick={() => handleProductChange(product)}
                          onMouseEnter={() => setActiveIndex(index)}
                        >
                          <span className="font-mono">{product}</span>
                          {product === selectedProduct && (
                            <span className="ml-2 text-[10px] text-primary">
                              Selected
                            </span>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}

                {!searchLoading &&
                  !searchError &&
                  normalizedQuery &&
                  searchResult &&
                  visibleProducts.length === 0 && (
                    <p className="px-3 py-4 text-sm text-text-muted">
                      No products match that code.
                    </p>
                  )}
              </div>
            )}
          </div>

          {selectedProduct && (
            <p className="mt-4 rounded-lg bg-surface-raised px-3 py-2 text-xs text-text-secondary">
              Selected SKU{" "}
              <span className="font-mono font-semibold text-primary">
                {selectedProduct}
              </span>
            </p>
          )}
        </section>

        {forecast && <ForecastCard forecast={forecast} />}
      </aside>
    </div>
  );
}
