"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import { APP_NAME } from "@/lib/constants";

export function Header() {
  const { user, logout } = useAuth();
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 px-4 h-14 flex items-center justify-between">
      <Link href="/" className="text-lg font-bold text-slate-900">
        {APP_NAME}
      </Link>
      <div className="flex items-center gap-3">
        {user ? (
          <>
            <span className="text-sm text-slate-500 hidden sm:block">{user.displayName}</span>
            <button
              onClick={handleLogout}
              className="text-sm text-slate-400 hover:text-slate-700 transition-colors"
            >
              로그아웃
            </button>
          </>
        ) : (
          <Link href="/login" className="text-sm font-medium text-slate-700 hover:text-slate-900">
            로그인
          </Link>
        )}
      </div>
    </header>
  );
}
