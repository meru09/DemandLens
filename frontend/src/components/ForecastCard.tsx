
import type { ForecastResponse } from "@/types/api";

type ForecastCardProps = {
  forecast: ForecastResponse;
};

export default function ForecastCard({
  forecast,
}: ForecastCardProps) {
  // Format the forecast date
  const formattedDate = new Date(
    `${forecast.forecast_date}T00:00:00Z`
  ).toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  });

  // Display a user-friendly forecasting model name
  const modelName =
    forecast.model === "moving_average_3"
      ? "3-week moving average"
      : forecast.model;

  return (
    <section
      aria-labelledby="forecast-title"
      className="mt-6 min-w-0 overflow-hidden rounded-xl border border-violet-700/40 bg-[#10101F]"
    >
      {/* Violet accent line */}
      <div className="h-1 bg-gradient-to-r from-violet-600 via-violet-400 to-transparent" />

      <div className="p-5 sm:p-6">
        {/* Forecast header */}
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <div className="mb-3 flex flex-wrap items-center gap-3">
              <p className="text-xs font-medium uppercase tracking-widest text-violet-400">
                Demand Prediction
              </p>

              <span className="rounded-full border border-violet-700/40 bg-violet-500/10 px-3 py-1 text-[10px] font-medium text-violet-200">
                Historical Data Demo
              </span>
            </div>

            <h3
              id="forecast-title"
              className="text-lg font-semibold text-white"
            >
              Next Week Forecast
            </h3>
          </div>

          {/* Decorative icon */}
          <div
            aria-hidden="true"
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-violet-700/30 bg-violet-500/10 text-xl text-violet-300"
          >
            ✦
          </div>
        </div>

        {/* Main prediction */}
        <div className="mt-7 rounded-xl border border-violet-700/20 bg-violet-500/5 p-5 sm:p-6">
          <p className="text-sm text-slate-400">
            Expected demand
          </p>

          <div className="mt-3 flex flex-wrap items-baseline gap-3">
            <p className="break-words text-5xl font-bold tracking-tight text-white sm:text-6xl">
              {forecast.predicted_units.toLocaleString()}
            </p>

            <span className="text-sm font-medium text-violet-300">
              units
            </span>
          </div>

          <p className="mt-4 text-xs text-slate-500">
            Predicted quantity for the next forecast week
          </p>
        </div>

        {/* Forecast details */}
        <div className="mt-6 space-y-4">
          {/* Forecast date */}
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-sm text-slate-400">
              Forecast week
            </span>

            <span className="text-sm font-medium text-white">
              {formattedDate}
            </span>
          </div>

          <div className="border-t border-violet-900/30" />

          {/* Forecasting model */}
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-sm text-slate-400">
              Forecasting model
            </span>

            <span className="rounded-md border border-violet-700/30 bg-violet-500/10 px-3 py-1 text-xs font-medium text-violet-300">
              {modelName}
            </span>
          </div>
        </div>

        {/* Historical data explanation */}
        <p className="mt-6 border-t border-violet-900/30 pt-4 text-xs leading-relaxed text-slate-500">
          This forecast estimates demand for the week
          following the product&apos;s last available
          historical sales observation. It is generated
          from a historical retail dataset for
          demonstration and evaluation purposes, not as
          a live prediction of current demand.
        </p>
      </div>
    </section>
  );
}
