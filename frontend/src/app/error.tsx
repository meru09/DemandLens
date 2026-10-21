
"use client";

import { useRouter } from "next/navigation";

export default function Error({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const router = useRouter();

  function handleRetry() {
    router.refresh();
    reset();
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#0B0B16] px-6 text-white">
      <div className="max-w-md text-center">
        <h1 className="text-3xl font-bold">
          Unable to load dashboard
        </h1>

        <p className="mt-4 text-slate-400">
          We couldn't retrieve your sales data.
          Please check your connection and try again.
        </p>

        <button
          onClick={handleRetry}
          className="mt-8 rounded-lg bg-violet-600 px-6 py-3 font-medium text-white transition hover:bg-violet-500"
        >
          Try Again
        </button>
      </div>
    </main>
  );
}
