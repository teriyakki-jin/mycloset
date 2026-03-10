"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/auth-context";
import { apiClient } from "@/lib/api-client";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await apiClient.post<{ accessToken: string }>("/auth/login", { email, password });
      await login(res.accessToken);
      router.push("/closet");
    } catch (err) {
      setError(err instanceof Error ? err.message : "로그인에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <h1 className="text-2xl font-bold text-slate-900 mb-1">로그인</h1>
        <p className="text-slate-400 text-sm mb-8">ClosetIQ에 오신 것을 환영합니다.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">이메일</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 bg-white"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">비밀번호</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="최소 8자"
              required
              className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 bg-white"
            />
          </div>

          {error && <p className="text-sm text-red-500">{error}</p>}

          <Button type="submit" loading={loading} className="w-full" size="lg">
            로그인
          </Button>
        </form>

        <p className="text-center text-sm text-slate-400 mt-6">
          계정이 없으신가요?{" "}
          <Link href="/register" className="text-slate-800 font-medium underline underline-offset-2">
            회원가입
          </Link>
        </p>
      </div>
    </div>
  );
}
