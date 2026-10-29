
"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);

  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const drawerRef = useRef<HTMLElement>(null);

  // Manage keyboard focus and background scrolling
  useEffect(() => {
    if (!isOpen) return;

    const menuButton = menuButtonRef.current;
    const previousOverflow = document.body.style.overflow;

    // Prevent background scrolling
    document.body.style.overflow = "hidden";

    // Move focus into the drawer
    closeButtonRef.current?.focus();

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        setIsOpen(false);
        return;
      }

      if (event.key !== "Tab") return;

      const drawer = drawerRef.current;
      if (!drawer) return;

      const focusableElements =
        drawer.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );

      const elements = Array.from(focusableElements);

      if (elements.length === 0) {
        event.preventDefault();
        return;
      }

      const firstElement = elements[0];
      const lastElement = elements[elements.length - 1];
      const activeElement = document.activeElement;

      // Keep keyboard focus inside the drawer
      if (
        !drawer.contains(activeElement) ||
        (event.shiftKey && activeElement === firstElement)
      ) {
        event.preventDefault();
        (event.shiftKey ? lastElement : firstElement).focus();
      } else if (
        !event.shiftKey &&
        activeElement === lastElement
      ) {
        event.preventDefault();
        firstElement.focus();
      }
    }

    document.addEventListener("keydown", handleKeyDown);

    return () => {
     document.body.style.overflow = previousOverflow;
     document.removeEventListener(
      "keydown",
      handleKeyDown
    );

    // Return focus to the original menu button
    menuButton?.focus();
   };
  }, [isOpen]);

  const navigation = (
    <>
      {/* Branding */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold text-white">
          Demand
          <span className="text-violet-400">
            Lens
          </span>
        </h2>

        <p className="mt-1 text-xs text-slate-500">
          Sales Intelligence
        </p>
      </div>

      {/* Navigation links */}
      <nav
        aria-label="Main navigation"
        className="space-y-2"
      >
        <Link
          href="/"
          aria-current="page"
          onClick={() => setIsOpen(false)}
          className="block rounded-lg bg-violet-600/20 px-4 py-3 text-sm font-medium text-violet-300"
        >
          Dashboard
        </Link>
      </nav>

      {/* Version */}
      <div className="mt-12 border-t border-violet-900/30 pt-6">
        <p className="text-xs text-slate-500">
          DemandLens v0.1
        </p>
      </div>
    </>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden w-64 shrink-0 border-r border-violet-900/30 bg-[#10101F] p-6 md:block">
        {navigation}
      </aside>

      {/* Mobile header */}
      <header className="fixed inset-x-0 top-0 z-30 flex h-16 items-center justify-between border-b border-violet-900/30 bg-[#10101F] px-5 md:hidden">
        <Link
          href="/"
          className="text-xl font-bold text-white"
        >
          Demand
          <span className="text-violet-400">
            Lens
          </span>
        </Link>

        <button
          ref={menuButtonRef}
          type="button"
          aria-label="Open navigation menu"
          aria-expanded={isOpen}
          aria-controls="mobile-navigation"
          onClick={() => setIsOpen(true)}
          className="rounded-lg border border-violet-800/50 p-2 text-violet-300 transition hover:bg-violet-600/20 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-400"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </header>

      {/* Mobile navigation drawer */}
      {isOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          {/* Backdrop */}
          <button
            type="button"
            aria-label="Close navigation menu"
            onClick={() => setIsOpen(false)}
            tabIndex={-1}
            className="absolute inset-0 h-full w-full bg-black/70"
          />

          {/* Drawer */}
          <aside
            ref={drawerRef}
            id="mobile-navigation"
            role="dialog"
            aria-modal="true"
            aria-label="Mobile navigation"
            className="absolute inset-y-0 left-0 w-72 max-w-[85vw] overflow-y-auto border-r border-violet-900/40 bg-[#10101F] p-6 shadow-2xl"
          >
            <div className="mb-8 flex justify-end">
              <button
                ref={closeButtonRef}
                type="button"
                aria-label="Close navigation menu"
                onClick={() => setIsOpen(false)}
                className="rounded-lg p-2 text-slate-300 transition hover:bg-violet-600/20 focus-visible:outline-2 focus-visible:outline-violet-400"
              >
                <svg
                  width="22"
                  height="22"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  aria-hidden="true"
                >
                  <path d="M18 6 6 18M6 6l12 12" />
                </svg>
              </button>
            </div>

            {navigation}
          </aside>
        </div>
      )}
    </>
  );
}
