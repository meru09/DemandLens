import DashboardHeader from "@/components/DashboardHeader";
import ProductSelector from "@/components/ProductSelector";
import Sidebar from "@/components/Sidebar";
import StatCard from "@/components/StatCard";
import { fetchApiJson } from "@/lib/api";

import type {
  DashboardSummaryResponse,
  ProductsResponse,
} from "@/types/api";

function isDashboardSummary(
  value: DashboardSummaryResponse
): boolean {
  return (
    Number.isFinite(value.weeks) &&
    value.weeks > 0 &&
    Number.isFinite(value.total_units_sold) &&
    Number.isFinite(value.total_products) &&
    Number.isFinite(value.total_transactions) &&
    Number.isFinite(value.average_units_per_week) &&
    /^\d{4}-\d{2}-\d{2}$/.test(value.dataset_start) &&
    /^\d{4}-\d{2}-\d{2}$/.test(value.dataset_end)
  );
}

function isProductsResponse(value: ProductsResponse): boolean {
  return (
    Number.isFinite(value.total_products) &&
    Array.isArray(value.products) &&
    value.products.every((product) => typeof product === "string")
  );
}

export default async function Home() {
  const [summary, productData] = await Promise.all([
    fetchApiJson<DashboardSummaryResponse>("/dashboard/summary"),
    fetchApiJson<ProductsResponse>("/products"),
  ]);

  if (!isDashboardSummary(summary)) {
    throw new Error("Invalid dashboard summary data received.");
  }
  if (!isProductsResponse(productData)) {
    throw new Error("Invalid product catalog data received.");
  }

  return (
    <div className="min-h-screen bg-background text-foreground md:flex">
      <Sidebar />

      <main className="min-w-0 flex-1 px-4 pb-10 pt-24 sm:px-6 md:px-8 md:py-10">
        <div className="mx-auto max-w-7xl">
          <DashboardHeader
            datasetStart={summary.dataset_start}
            datasetEnd={summary.dataset_end}
          />

          <section aria-label="Historical dataset summary">
            <div className="mb-4 flex flex-wrap items-end justify-between gap-2">
              <h2 className="font-display text-lg font-semibold text-foreground">
                Dataset overview
              </h2>
              <p className="text-xs text-text-muted">
                {summary.weeks.toLocaleString("en-US")} weekly observations
                across the full dataset
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <StatCard
                title="Total units sold"
                value={summary.total_units_sold.toLocaleString("en-US")}
                description="Sum of recorded weekly units"
                icon="units"
              />
              <StatCard
                title="Products"
                value={summary.total_products.toLocaleString("en-US")}
                description="Unique product codes in the dataset"
                icon="products"
              />
              <StatCard
                title="Transactions"
                value={summary.total_transactions.toLocaleString("en-US")}
                description="Distinct cleaned invoices; cancellations excluded"
                icon="transactions"
              />
              <StatCard
                title="Average units per week"
                value={summary.average_units_per_week.toLocaleString(
                  "en-US",
                  { maximumFractionDigits: 1 }
                )}
                description="Total units divided by recorded dataset weeks"
                icon="weekly"
              />
            </div>
          </section>

          <section
            aria-labelledby="product-analysis-heading"
            className="mt-10"
          >
            <div className="mb-5">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                Product-level analysis
              </p>
              <h2
                id="product-analysis-heading"
                className="mt-2 font-display text-xl font-semibold text-foreground"
              >
                Explore demand
              </h2>
            </div>
            <ProductSelector
              products={productData.products}
              totalProducts={summary.total_products}
            />
          </section>
        </div>
      </main>
    </div>
  );
}
