import Link from "next/link";
import { APP_NAME } from "@/lib/constants";

export function Header() {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 px-4 h-14 flex items-center justify-between">
      <Link href="/" className="text-lg font-bold text-slate-900">
        {APP_NAME}
      </Link>
    </header>
  );
}
