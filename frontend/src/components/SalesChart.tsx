
"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import type { WeeklySale } from "@/types/api";

// Format dates for chart labels
function formatDate(dateString: string) {
  const [year, month, day] = dateString
    .split("-")
    .map(Number);

  return new Date(
    Date.UTC(year, month - 1, day)
  ).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  });
}

// Format full dates for tooltip
function formatFullDate(dateString: string) {
  const [year, month, day] = dateString
    .split("-")
    .map(Number);

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
};

export default function SalesChart({
  data,
}: SalesChartProps) {
  return (
    <div className="mt-6 min-w-0 overflow-hidden rounded-xl border border-violet-900/40 bg-[#171728] p-4 sm:p-6">
      {/* Chart header */}
      <h3 className="mb-2 text-base font-semibold text-white sm:text-lg">
        Weekly Sales History
      </h3>

      <p className="mb-5 text-xs text-slate-400 sm:mb-6 sm:text-sm">
        Historical product demand over time
      </p>

      {/* Responsive chart container */}
      <div className="h-64 min-w-0 w-full sm:h-80">
        <ResponsiveContainer
          width="100%"
          height="100%"
          minWidth={0}
        >
          <LineChart
            data={data}
            margin={{
              top: 10,
              right: 8,
              left: -20,
              bottom: 5,
            }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#303047"
              vertical={false}
            />

            <XAxis
              dataKey="InvoiceDate"
              stroke="#94A3B8"
              tick={{ fontSize: 10 }}
              minTickGap={35}
              tickFormatter={formatDate}
              tickLine={false}
              axisLine={false}
            />

            <YAxis
              stroke="#94A3B8"
              tick={{ fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              allowDecimals={false}
              width={55}
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
              formatter={(value) => [
                Number(value).toLocaleString(),
                "Units Sold",
              ]}
              contentStyle={{
                backgroundColor: "#171728",
                border: "1px solid #303047",
                borderRadius: "8px",
                color: "#FFFFFF",
                fontSize: "12px",
              }}
              labelStyle={{
                color: "#C4B5FD",
                fontWeight: 600,
              }}
            />

            <Line
              type="linear"
              dataKey="UnitsSold"
              name="Units Sold"
              stroke="#A78BFA"
              strokeWidth={2}
              dot={false}
              activeDot={{
                r: 5,
                fill: "#A78BFA",
                stroke: "#FFFFFF",
                strokeWidth: 2,
              }}
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
