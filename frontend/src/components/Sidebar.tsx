
import Link from "next/link";

export default function Sidebar() {
  return (

      <aside className="hidden w-64 shrink-0 border-r border-violet-900/30 bg-[#10101F] p-6 md:block">
      <div className="mb-12">
        <h2 className="text-2xl font-bold text-white">
          Demand<span className="text-violet-400">Lens</span>
        </h2>
        <p className="mt-1 text-xs text-slate-500">
          Sales Intelligence
        </p>
      </div>

      <nav className="space-y-2">
        <Link
          href="/"
          className="block rounded-lg bg-violet-600/20 px-4 py-3 text-sm font-medium text-violet-300"
        >
          Dashboard
        </Link>
      </nav>

      <div className="mt-12 border-t border-violet-900/30 pt-6">
        <p className="text-xs text-slate-500">
          DemandLens v0.1
        </p>
      </div>
    </aside>
  );
}
