"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ClothingCard } from "@/components/closet/clothing-card";
import type { Garment, GarmentCategory } from "@/types";
import { apiClient } from "@/lib/api-client";

const CATEGORIES: { label: string; value: GarmentCategory | "all" }[] = [
  { label: "전체", value: "all" },
  { label: "상의", value: "top" },
  { label: "하의", value: "bottom" },
  { label: "아우터", value: "outer" },
  { label: "원피스", value: "dress" },
  { label: "신발", value: "shoes" },
  { label: "가방", value: "bag" },
  { label: "액세서리", value: "accessory" },
];

export default function ClosetPage() {
  const [garments, setGarments] = useState<Garment[]>([]);
  const [total, setTotal] = useState(0);
  const [category, setCategory] = useState<GarmentCategory | "all">("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    setLoading(true);
    const params = new URLSearchParams({ limit: "40" });
    if (category !== "all") params.set("category", category);

    apiClient
      .get<{ items: Garment[]; total: number }>(`/garments?${params}`, { token })
      .then((data) => {
        setGarments(data.items);
        setTotal(data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [category]);

  return (
    <div className="px-4 py-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-slate-900">내 옷장 {total > 0 && <span className="text-slate-400 font-normal text-base">({total})</span>}</h2>
        <Link href="/upload" className="text-sm font-medium text-slate-500 hover:text-slate-800">
          + 추가
        </Link>
      </div>

      {/* 카테고리 필터 */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-4 scrollbar-hide">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.value}
            onClick={() => setCategory(cat.value)}
            className={`shrink-0 text-xs font-medium px-3 py-1.5 rounded-full border transition-colors ${
              category === cat.value
                ? "bg-slate-900 text-white border-slate-900"
                : "bg-white text-slate-600 border-slate-200 hover:border-slate-400"
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="aspect-[3/4] rounded-xl bg-slate-100 animate-pulse" />
          ))}
        </div>
      ) : garments.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <p className="text-4xl mb-3">👗</p>
          <p className="text-slate-500 text-sm">아직 등록된 옷이 없습니다.</p>
          <Link
            href="/upload"
            className="mt-4 text-sm font-medium text-slate-900 underline underline-offset-2"
          >
            첫 번째 옷 추가하기
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {garments.map((g) => (
            <ClothingCard key={g.id} garment={g} />
          ))}
        </div>
      )}
    </div>
  );
}
