"use client";

export default function Error({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 text-foreground">
      <div className="max-w-md rounded-2xl border border-border/70 bg-surface-card p-8 text-center">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-danger">
          Dashboard unavailable
        </p>
        <h1 className="mt-3 font-display text-2xl font-semibold">
          Unable to load sales data
        </h1>
        <p className="mt-4 text-sm leading-relaxed text-text-secondary">
          Check that the DemandLens API is running, then try loading the
          dashboard again.
        </p>
        <button
          type="button"
          onClick={() => reset()}
          className="mt-6 rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-background transition hover:bg-primary-strong focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
        >
          Try again
        </button>
      </div>
    </main>
  );
}
