"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/auth-context";
import { apiClient } from "@/lib/api-client";

export default function RegisterPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await apiClient.post("/auth/register", { email, password, display_name: displayName });
      const res = await apiClient.post<{ access_token: string }>("/auth/login", { email, password });
      await login(res.access_token);
      router.push("/closet");
    } catch (err) {
      setError(err instanceof Error ? err.message : "회원가입에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <h1 className="text-2xl font-bold text-slate-900 mb-1">회원가입</h1>
        <p className="text-slate-400 text-sm mb-8">AI 옷장 관리를 시작해보세요.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">닉네임</label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="홍길동"
              required
              className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 bg-white"
            />
          </div>
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
              minLength={8}
              className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 bg-white"
            />
          </div>

          {error && <p className="text-sm text-red-500">{error}</p>}

          <Button type="submit" loading={loading} className="w-full" size="lg">
            시작하기
          </Button>
        </form>

        <p className="text-center text-sm text-slate-400 mt-6">
          이미 계정이 있으신가요?{" "}
          <Link href="/login" className="text-slate-800 font-medium underline underline-offset-2">
            로그인
          </Link>
        </p>
      </div>
    </div>
  );
}
