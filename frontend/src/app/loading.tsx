
export default function Loading() {
  return (
    <main className="min-h-screen bg-background px-5 py-10 text-foreground sm:px-8">
      <div className="mx-auto max-w-7xl">
        <p className="mb-3 text-xs font-semibold tracking-[0.24em] text-primary">
          RETAIL INTELLIGENCE
        </p>
        <h1 className="font-display text-3xl font-semibold sm:text-4xl">
          DemandLens Dashboard
        </h1>
        <p className="mt-3 text-sm text-text-secondary">
          Loading real sales data…
        </p>

        <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }, (_, index) => (
            <div
              key={index}
              className="h-36 animate-pulse rounded-2xl border border-border/70 bg-surface-card"
            />
          ))}
        </div>
      </div>
    </main>
  );
}
