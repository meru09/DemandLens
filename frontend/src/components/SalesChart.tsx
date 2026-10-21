
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

// Format dates for display
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

// Format dates for the tooltip
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
};

export default function SalesChart({
  data,
}: SalesChartProps) {
  return (
    <div className="mt-6 rounded-xl border border-violet-900/40 bg-[#171728] p-6">
      <h3 className="mb-2 text-lg font-semibold text-white">
        Weekly Sales History
      </h3>

      <p className="mb-6 text-sm text-slate-400">
        Historical product demand over time
      </p>

      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{
              top: 10,
              right: 20,
              left: 0,
              bottom: 10,
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
              tick={{ fontSize: 11 }}
              minTickGap={30}
              tickFormatter={formatDate}
              tickLine={false}
            />

            <YAxis
              stroke="#94A3B8"
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              allowDecimals={false}
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
