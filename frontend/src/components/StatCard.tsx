
type StatCardProps = {
  title: string;
  value: string;
  description: string;
  icon: "units" | "products" | "transactions" | "weekly";
};

export default function StatCard({
  title,
  value,
  description,
  icon,
}: StatCardProps) {
  return (
    <article className="min-w-0 rounded-2xl border border-border/70 bg-surface-card p-5 sm:p-6">
      <div className="flex items-start justify-between gap-4">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-surface-elevated text-primary">
          <svg
            aria-hidden="true"
            className="h-5 w-5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            {icon === "units" && (
              <>
                <path d="M4 19V5" />
                <path d="M4 19h16" />
                <path d="m7 14 4-4 3 2 5-6" />
              </>
            )}
            {icon === "products" && (
              <>
                <path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z" />
                <path d="m4.5 7.8 7.5 4.3 7.5-4.3" />
                <path d="M12 12v9" />
              </>
            )}
            {icon === "transactions" && (
              <>
                <rect x="4" y="3" width="16" height="18" rx="2" />
                <path d="M8 8h8M8 12h8M8 16h4" />
              </>
            )}
            {icon === "weekly" && (
              <>
                <circle cx="12" cy="12" r="9" />
                <path d="M12 7v5l3 2" />
              </>
            )}
          </svg>
        </div>
        <span className="rounded-full border border-border px-2.5 py-1 text-[10px] font-medium uppercase tracking-[0.14em] text-text-muted">
          Historical
        </span>
      </div>

      <p className="mt-5 text-sm font-medium text-text-secondary">
        {title}
      </p>
      <p className="mt-2 break-words font-display text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
        {value}
      </p>
      <p className="mt-2 text-xs leading-relaxed text-text-muted">
        {description}
      </p>
    </article>
  );
}
