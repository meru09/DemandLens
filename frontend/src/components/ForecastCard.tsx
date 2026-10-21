
import type { ForecastResponse } from "@/types/api";

type ForecastCardProps = {
  forecast: ForecastResponse;
};

export default function ForecastCard({
  forecast,
}: ForecastCardProps) {
  const formattedDate = new Date(
    `${forecast.forecast_date}T00:00:00Z`
  ).toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  });

  const modelName =
    forecast.model === "moving_average_3"
      ? "3-week moving average"
      : forecast.model;

  return (
    <div className="mt-6 rounded-xl border border-violet-700/40 bg-[#10101F] p-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-violet-300">
          Next Week Forecast
        </h3>

        <span className="text-2xl">✦</span>
      </div>

      <div className="mt-5 flex items-baseline gap-2">
        <p className="text-4xl font-bold text-white">
          {forecast.predicted_units.toLocaleString()}
        </p>

        <span className="text-sm text-slate-400">
          predicted units
        </span>
      </div>

      <div className="mt-6 space-y-3 border-t border-violet-900/40 pt-5">
        <div className="flex items-center justify-between gap-4">
          <span className="text-sm text-slate-400">
            Forecast week
          </span>

          <span className="text-sm font-medium text-white">
            {formattedDate}
          </span>
        </div>

        <div className="flex items-center justify-between gap-4">
          <span className="text-sm text-slate-400">
            Model
          </span>

          <span className="text-sm font-medium text-violet-300">
            {modelName}
          </span>
        </div>
      </div>

      <p className="mt-5 text-xs text-slate-500">
        Prediction for the week after the last available
        historical sales observation.
      </p>
    </div>
  );
}
