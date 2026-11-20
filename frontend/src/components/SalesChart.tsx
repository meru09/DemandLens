"use client";

import { useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type {
  ForecastHorizonResponse,
  WeeklySale,
} from "@/types/api";

const HISTORY_WINDOWS = [
  { weeks: 4, label: "4W" },
  { weeks: 12, label: "12W" },
  { weeks: 26, label: "26W" },
  { weeks: 52, label: "1Y" },
];

function formatDate(dateString: string) {
  const [year, month, day] = dateString.split("-").map(Number);

  return new Date(
    Date.UTC(year, month - 1, day)
  ).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  });
}

function formatFullDate(dateString: string) {
  const [year, month, day] = dateString.split("-").map(Number);

  return new Date(
    Date.UTC(year, month - 1, day)
  ).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  });
}

type SalesChartProps = {
  data: WeeklySale[];
  forecast: ForecastHorizonResponse | null;
};

export default function SalesChart({
  data,
  forecast,
}: SalesChartProps) {
  const [historyWindow, setHistoryWindow] = useState(12);
  const history = data.slice(-historyWindow);
  const points = forecast?.forecasts ?? [];
  const lastHistory = history.at(-1);
  const forecastMatchesHistory =
    lastHistory?.InvoiceDate === forecast?.forecast_origin;

  const chartData = [
    ...history.map((week, index) => ({
      date: week.InvoiceDate,
      actual: week.UnitsSold,
      predicted:
        index === history.length - 1 && forecastMatchesHistory
          ? week.UnitsSold
          : undefined,
    })),
    ...(forecastMatchesHistory
      ? points.map((point) => ({
          date: point.forecast_date,
          actual: undefined,
          predicted: point.predicted_units,
        }))
      : []),
  ];

  return (
    <section
      aria-labelledby="demand-chart-title"
      className="min-w-0 overflow-hidden rounded-2xl border border-border/70 bg-surface-card p-4 sm:p-6"
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2
            id="demand-chart-title"
            className="font-display text-lg font-semibold text-foreground"
          >
            Demand forecast
          </h2>
          <p className="mt-1 text-xs text-text-muted sm:text-sm">
            Observed sales and the next three forecast weeks
          </p>
        </div>

        <div
          aria-label="Historical chart window"
          className="inline-flex w-fit rounded-lg border border-border bg-surface-raised p-1"
        >
          {HISTORY_WINDOWS.map((option) => (
            <button
              key={option.weeks}
              type="button"
              aria-pressed={historyWindow === option.weeks}
              onClick={() => setHistoryWindow(option.weeks)}
              className={`rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary ${
                historyWindow === option.weeks
                  ? "bg-surface-active text-primary"
                  : "text-text-muted hover:text-foreground"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-6 h-64 min-w-0 w-full sm:h-80">
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <LineChart
            data={chartData}
            margin={{ top: 10, right: 12, left: -12, bottom: 4 }}
          >
            <CartesianGrid
              stroke="var(--border)"
              strokeDasharray="3 5"
              vertical={false}
            />
            <XAxis
              dataKey="date"
              stroke="var(--text-muted)"
              tick={{ fontSize: 10 }}
              minTickGap={28}
              tickFormatter={formatDate}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="var(--text-muted)"
              tick={{ fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              allowDecimals={false}
              width={48}
              tickFormatter={(value: number) =>
                value >= 1000
                  ? `${(value / 1000).toFixed(1)}k`
                  : String(value)
              }
            />
            <Tooltip
              labelFormatter={(label) =>
                formatFullDate(String(label))
              }
              formatter={(value, name) => [
                Number(value).toLocaleString("en-US", {
                  maximumFractionDigits: 1,
                }),
                name === "predicted"
                  ? "Predicted units"
                  : "Observed units",
              ]}
              contentStyle={{
                backgroundColor: "var(--surface-elevated)",
                border: "1px solid var(--border)",
                borderRadius: "12px",
                color: "var(--foreground)",
                fontSize: "12px",
              }}
              labelStyle={{
                color: "var(--text-secondary)",
                fontWeight: 600,
              }}
            />
            {forecastMatchesHistory && points.length > 0 && (
              <ReferenceLine
                x={points[0].forecast_date}
                stroke="var(--forecast)"
                strokeDasharray="4 4"
              />
            )}
            <Line
              type="monotone"
              dataKey="actual"
              name="Observed units"
              stroke="var(--primary)"
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 4, fill: "var(--primary)" }}
            />
            <Line
              type="monotone"
              dataKey="predicted"
              name="Predicted units"
              stroke="var(--forecast)"
              strokeWidth={2.5}
              strokeDasharray="6 5"
              dot={{ r: 3, fill: "var(--forecast)" }}
              activeDot={{ r: 5, fill: "var(--forecast)" }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-text-secondary">
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-primary" />
          Observed demand
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="w-5 border-t-2 border-dashed border-forecast" />
          Three-week forecast
        </span>
      </div>
    </section>
  );
}
