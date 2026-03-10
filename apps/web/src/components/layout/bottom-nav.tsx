"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/closet", label: "옷장", icon: "👗" },
  { href: "/upload", label: "등록", icon: "➕" },
  { href: "/outfit", label: "코디", icon: "✨" },
  { href: "/style-report", label: "리포트", icon: "📊" },
] as const;

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-slate-200 safe-area-pb">
      <ul className="flex">
        {NAV_ITEMS.map(({ href, label, icon }) => {
          const isActive = pathname.startsWith(href);
          return (
            <li key={href} className="flex-1">
              <Link
                href={href}
                className={`flex flex-col items-center justify-center gap-0.5 py-2 text-xs font-medium transition-colors ${
                  isActive ? "text-slate-900" : "text-slate-400"
                }`}
              >
                <span className="text-xl leading-none">{icon}</span>
                {label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
