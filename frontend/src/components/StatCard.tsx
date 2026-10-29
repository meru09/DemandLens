
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
    <div className="min-w-0 rounded-xl border border-violet-900/40 bg-[#171728] p-4 sm:p-6">
      <p className="text-sm text-slate-400">
        {title}
      </p>

      <h2 className="mt-3 break-words text-2xl font-bold text-white sm:text-3xl">
        {value}
      </h2>

      <p className="mt-2 text-xs text-slate-500">
        {description}
      </p>
    </div>
  );
}
