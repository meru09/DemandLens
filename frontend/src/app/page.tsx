
import StatCard from "@/components/StatCard";
import Sidebar from "@/components/Sidebar";
import ProductSelector from "@/components/ProductSelector";



type ProductsResponse = {
  total_products: number;
  products: string[];
};

export default async function Home() {
  const response = await fetch(
    "http://127.0.0.1:8000/products",
    { cache: "no-store" }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch products");
  }

  const data: ProductsResponse = await response.json();

  return (
    <div className="flex min-h-screen bg-[#0B0B16] text-white">

      {/* Sidebar */}
      <Sidebar />

      {/* Main Dashboard */}
      <main className="min-w-0 flex-1 px-8 py-12">
        <div className="mx-auto max-w-6xl">

          {/* Dashboard Header */}
          <p className="mb-3 text-sm font-medium tracking-[0.3em] text-violet-400">
            INTELLIGENT SALES ANALYTICS
          </p>

          <h1 className="text-4xl font-bold">
            DemandLens Dashboard
          </h1>

          <p className="mt-3 text-slate-400">
            Understand your sales and forecast future demand.
          </p>

          {/* Statistics Cards */}
          <div className="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-3">

            <StatCard
              title="Total Products"
              value={data.total_products.toLocaleString()}
              description="Products in our sales dataset"
            />

            <StatCard
              title="Total Units Sold"
              value="11,403,162"
              description="Units sold in the historical dataset"
            />

          </div>
          
          {/* Product Selection */}
          <section className="mt-10">
            <h2 className="mb-4 text-xl font-semibold text-white">
                 Product Analysis
            </h2>

            <ProductSelector products={data.products}/>
           </section>

        </div>
      </main>
    </div>
  );
}
