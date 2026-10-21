
export default function Loading() {
  return (
    <main className="min-h-screen bg-[#0B0B16] px-8 py-12 text-white">
      <div className="mx-auto max-w-6xl">
        <p className="mb-3 text-sm font-medium tracking-[0.3em] text-violet-400">
          INTELLIGENT SALES ANALYTICS
        </p>

        <h1 className="text-4xl font-bold">
          DemandLens Dashboard
        </h1>

        <p className="mt-3 text-slate-400">
          Loading your sales insights...
        </p>

        <div className="mt-10 grid gap-6 md:grid-cols-3">
          <div className="h-36 animate-pulse rounded-xl border border-violet-900/40 bg-[#171728]" />
        </div>
      </div>
    </main>
  );
}
