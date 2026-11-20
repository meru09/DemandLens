type DashboardHeaderProps = {
  datasetStart: string;
  datasetEnd: string;
};

function formatDate(value: string) {
  return new Date(`${value}T00:00:00Z`).toLocaleDateString(
    "en-US",
    {
      month: "short",
      year: "numeric",
      timeZone: "UTC",
    }
  );
}

export default function DashboardHeader({
  datasetStart,
  datasetEnd,
}: DashboardHeaderProps) {
  return (
    <header className="mb-8 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p className="mb-3 text-xs font-semibold tracking-[0.24em] text-primary">
          RETAIL INTELLIGENCE
        </p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          DemandLens Dashboard
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed text-text-secondary">
          Explore observed sales and a three-week product demand forecast.
        </p>
        <p className="mt-2 text-xs text-text-muted">
          Historical dataset: {formatDate(datasetStart)} –{" "}
          {formatDate(datasetEnd)}
        </p>
      </div>

      <div className="inline-flex w-fit items-center gap-2 rounded-full border border-forecast/30 bg-forecast/10 px-3 py-2 text-xs font-medium text-forecast">
        <span
          aria-hidden="true"
          className="h-1.5 w-1.5 rounded-full bg-forecast"
        />
        3-week forecast horizon
      </div>
    </header>
  );
}
