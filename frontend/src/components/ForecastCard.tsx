import type { ForecastHorizonResponse } from "@/types/api";

type ForecastCardProps = {
  forecast: ForecastHorizonResponse;
};

function formatDate(value: string) {
  return new Date(`${value}T00:00:00Z`).toLocaleDateString(
    "en-US",
    {
      month: "short",
      day: "numeric",
      year: "numeric",
      timeZone: "UTC",
    }
  );
}

function formatUnits(value: number) {
  return value.toLocaleString("en-US", {
    maximumFractionDigits: 1,
  });
}

function modelLabel(model: string) {
  if (model === "moving_average_3_recursive") {
    return "Recursive 3-week moving average";
  }
  return model;
}

export default function ForecastCard({
  forecast,
}: ForecastCardProps) {
  const totalPredictedUnits = forecast.forecasts.reduce(
    (total, point) => total + point.predicted_units,
    0
  );

  return (
    <section
      aria-labelledby="forecast-summary-title"
      className="overflow-hidden rounded-2xl border border-border/70 bg-surface-card"
    >
      <div className="h-1 bg-gradient-to-r from-forecast via-primary to-transparent" />
      <div className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-forecast">
              Product outlook
            </p>
            <h2
              id="forecast-summary-title"
              className="mt-2 font-display text-lg font-semibold text-foreground"
            >
              Next three weeks
            </h2>
          </div>
          <span className="rounded-full border border-border px-2.5 py-1 text-[10px] text-text-muted">
            Historical data
          </span>
        </div>

        <div className="mt-5 rounded-xl bg-surface-raised p-4">
          <p className="text-xs text-text-muted">
            Predicted units across the three weeks
          </p>
          <p className="mt-2 font-display text-3xl font-semibold text-foreground">
            {formatUnits(totalPredictedUnits)}
          </p>
        </div>

        <div className="mt-5 overflow-hidden rounded-xl border border-border/70">
          <div className="grid grid-cols-[0.6fr_1.4fr_0.8fr] gap-2 bg-surface-elevated px-3 py-2.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-text-muted">
            <span>Week</span>
            <span>Forecast date</span>
            <span className="text-right">Units</span>
          </div>
          <ol className="divide-y divide-border/70">
            {forecast.forecasts.map((point, index) => (
              <li
                key={point.forecast_date}
                className="grid grid-cols-[0.6fr_1.4fr_0.8fr] items-center gap-2 px-3 py-3 text-xs"
              >
                <span className="font-mono text-forecast">
                  W+{index + 1}
                </span>
                <time
                  dateTime={point.forecast_date}
                  className="text-text-secondary"
                >
                  {formatDate(point.forecast_date)}
                </time>
                <span className="text-right font-mono text-foreground">
                  {formatUnits(point.predicted_units)}
                </span>
              </li>
            ))}
          </ol>
        </div>

        <dl className="mt-5 space-y-3 text-xs">
          <div className="flex items-start justify-between gap-3">
            <dt className="text-text-muted">Forecast origin</dt>
            <dd className="text-right text-text-secondary">
              {formatDate(forecast.forecast_origin)}
            </dd>
          </div>
          <div className="flex items-start justify-between gap-3">
            <dt className="text-text-muted">Model</dt>
            <dd className="max-w-[65%] text-right text-text-secondary">
              {modelLabel(forecast.model)}
            </dd>
          </div>
        </dl>

        <p className="mt-5 border-t border-border/70 pt-4 text-xs leading-relaxed text-text-muted">
          Forecast dates follow the latest available weekly observation in the
          historical dataset; they are not current-date demand guarantees.
        </p>
      </div>
    </section>
  );
}
