
type StatCardProps = {
  title: string;
  value: string;
  description: string;
};

export default function StatCard({
  title,
  value,
  description,
}: StatCardProps) {
  return (
    <div className="rounded-xl border border-violet-900/40 bg-[#171728] p-6">
      <p className="text-sm text-slate-400">
        {title}
      </p>

      <h2 className="mt-3 text-3xl font-bold text-white">
        {value}
      </h2>

      <p className="mt-2 text-xs text-slate-500">
        {description}
      </p>
    </div>
  );
}
