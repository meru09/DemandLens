import type {
  ForecastHorizonMetric,
  ProductForecastEvaluationResponse,
  ProductHistoryResponse,
} from "@/types/api";

type InsightCardsProps = {
  history: ProductHistoryResponse;
  evaluation: ProductForecastEvaluationResponse | null;
  evaluationError: string;
};

function formatNumber(value: number) {
  return value.toLocaleString("en-US", {
    maximumFractionDigits: 1,
  });
}

function getTrend(history: ProductHistoryResponse) {
  const recent = history.history.slice(-12);
  const previous = history.history.slice(-24, -12);

  if (recent.length < 12 || previous.length < 12) {
    return null;
  }

  const recentUnits = recent.reduce(
    (total, week) => total + week.UnitsSold,
    0
  );
  const previousUnits = previous.reduce(
    (total, week) => total + week.UnitsSold,
    0
  );

  if (previousUnits === 0) {
    return {
      recentUnits,
      previousUnits,
      percentage: null,
    };
  }

  return {
    recentUnits,
    previousUnits,
    percentage:
      ((recentUnits - previousUnits) / previousUnits) * 100,
  };
}

function getThreeWeekMetric(
  evaluation: ProductForecastEvaluationResponse | null
): ForecastHorizonMetric | null {
  return (
    evaluation?.metrics.find((metric) => metric.horizon_weeks === 3) ??
    null
  );
}

export default function InsightCards({
  history,
  evaluation,
  evaluationError,
}: InsightCardsProps) {
  const trend = getTrend(history);
  const metric = getThreeWeekMetric(evaluation);
  const modelWon =
    metric?.moving_average_mae !== null &&
    metric?.moving_average_mae !== undefined &&
    metric.naive_mae !== null &&
    metric.naive_mae !== undefined &&
    metric.moving_average_mae <= metric.naive_mae;
  const modelComparison =
    metric?.moving_average_mae === null ||
    metric?.moving_average_mae === undefined ||
    metric.naive_mae === null
      ? null
      : metric.moving_average_mae < metric.naive_mae
        ? `lower MAE than the last-value baseline (${formatNumber(metric.moving_average_mae)} vs. ${formatNumber(metric.naive_mae)} units)`
        : metric.moving_average_mae > metric.naive_mae
          ? `higher MAE than the last-value baseline (${formatNumber(metric.moving_average_mae)} vs. ${formatNumber(metric.naive_mae)} units)`
          : "the same MAE as the last-value baseline";

  return (
    <div className="mt-5 grid gap-4 lg:grid-cols-2">
      <article className="rounded-2xl border border-border/70 bg-surface-card p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold text-foreground">
              Forecast model performance
            </p>
            <p className="mt-1 text-xs text-text-muted">
              Rolling-origin evaluation at the 3-week lead
            </p>
          </div>
          {metric && metric.evaluation_origins > 0 && (
            <span className="shrink-0 rounded-full bg-surface-elevated px-2.5 py-1 text-[10px] text-text-secondary">
              {metric.evaluation_origins} origins
            </span>
          )}
        </div>

        {metric?.moving_average_mae !== null &&
        metric?.moving_average_mae !== undefined &&
        metric.moving_average_rmse !== null ? (
          <>
            <div className="mt-5 grid grid-cols-2 gap-3">
              <div className="rounded-xl bg-surface-raised p-3">
                <p className="font-mono text-[10px] tracking-wide text-text-muted">
                  MAE · UNITS
                </p>
                <p className="mt-2 font-display text-2xl font-semibold text-foreground">
                  {formatNumber(metric.moving_average_mae)}
                </p>
              </div>
              <div className="rounded-xl bg-surface-raised p-3">
                <p className="font-mono text-[10px] tracking-wide text-text-muted">
                  RMSE · UNITS
                </p>
                <p className="mt-2 font-display text-2xl font-semibold text-foreground">
                  {formatNumber(metric.moving_average_rmse)}
                </p>
              </div>
            </div>
            <p className="mt-4 text-xs leading-relaxed text-text-secondary">
              Recursive 3-week moving average has{" "}
              <span
                className={
                  modelWon ? "text-primary" : "text-text-secondary"
                }
              >
                {modelComparison}
              </span>
              .
            </p>
          </>
        ) : evaluationError ? (
          <p className="mt-5 rounded-xl bg-surface-raised p-4 text-sm leading-relaxed text-text-secondary">
            Backtest metrics unavailable: {evaluationError}
          </p>
        ) : (
          <p className="mt-5 rounded-xl bg-surface-raised p-4 text-sm leading-relaxed text-text-secondary">
            Three-week accuracy is unavailable because the product does not
            have enough held-out history for a backtest.
          </p>
        )}
      </article>

      <article className="rounded-2xl border border-border/70 bg-surface-card p-5">
        <div>
          <p className="text-sm font-semibold text-foreground">
            Demand trend
          </p>
          <p className="mt-1 text-xs text-text-muted">
            Latest 12 observed weeks vs. the previous 12
          </p>
        </div>

        {trend ? (
          <>
            <p className="mt-5 font-display text-3xl font-semibold text-foreground">
              {trend.percentage === null
                ? "—"
                : `${trend.percentage >= 0 ? "+" : ""}${trend.percentage.toFixed(1)}%`}
            </p>
            <p className="mt-2 text-sm text-text-secondary">
              {formatNumber(trend.recentUnits)} units recently, compared with{" "}
              {formatNumber(trend.previousUnits)} units in the prior 12 weeks.
            </p>
          </>
        ) : (
          <p className="mt-5 rounded-xl bg-surface-raised p-4 text-sm leading-relaxed text-text-secondary">
            At least 24 observed weeks are needed to compare two 12-week
            periods.
          </p>
        )}
      </article>
    </div>
  );
}
