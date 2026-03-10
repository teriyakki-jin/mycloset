"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api-client";
import type { Garment, GarmentCategory, Season } from "@/types";

const SEASON_LABEL: Record<Season, string> = {
  spring: "봄",
  summer: "여름",
  autumn: "가을",
  winter: "겨울",
};

const CATEGORY_LABEL: Record<GarmentCategory, string> = {
  top: "상의",
  bottom: "하의",
  outer: "아우터",
  dress: "원피스",
  shoes: "신발",
  bag: "가방",
  accessory: "액세서리",
  etc: "기타",
};

export default function GarmentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [garment, setGarment] = useState<Garment | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    apiClient
      .get<Garment>(`/garments/${id}`, { token })
      .then(setGarment)
      .catch(() => router.push("/closet"))
      .finally(() => setLoading(false));
  }, [id, router]);

  if (loading) {
    return (
      <div className="px-4 py-5">
        <div className="aspect-[3/4] rounded-2xl bg-slate-100 animate-pulse mb-4" />
        <div className="h-6 bg-slate-100 rounded animate-pulse mb-2 w-2/3" />
        <div className="h-4 bg-slate-100 rounded animate-pulse w-1/3" />
      </div>
    );
  }

  if (!garment) return null;

  const imageUrl = garment.cutoutImageUrl ?? garment.originalImageUrl;

  return (
    <div className="px-4 py-5 max-w-md mx-auto">
      <button onClick={() => router.back()} className="text-sm text-slate-500 mb-4">
        ← 뒤로
      </button>

      <div className="relative aspect-[3/4] rounded-2xl overflow-hidden bg-slate-100 mb-5">
        <Image src={imageUrl} alt={garment.name} fill className="object-cover" />
      </div>

      <h2 className="text-xl font-bold text-slate-900 mb-1">{garment.name}</h2>

      <div className="flex flex-wrap gap-1.5 mt-3">
        {garment.category && (
          <span className="text-xs bg-slate-100 text-slate-700 px-2.5 py-1 rounded-full">
            {CATEGORY_LABEL[garment.category as GarmentCategory] ?? garment.category}
          </span>
        )}
        {garment.seasons.map((s) => (
          <span key={s} className="text-xs bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full">
            {SEASON_LABEL[s as Season] ?? s}
          </span>
        ))}
        {garment.styleTags.map((tag) => (
          <span key={tag} className="text-xs bg-slate-50 text-slate-500 px-2.5 py-1 rounded-full border border-slate-200">
            #{tag}
          </span>
        ))}
      </div>

      {garment.dominantColors.length > 0 && (
        <div className="mt-4">
          <p className="text-xs text-slate-400 mb-1.5">대표 색상</p>
          <div className="flex gap-2">
            {garment.dominantColors.map((color) => (
              <div
                key={color}
                className="w-7 h-7 rounded-full border border-slate-200 shadow-sm"
                style={{ backgroundColor: color }}
                title={color}
              />
            ))}
          </div>
        </div>
      )}

      <div className="mt-4 text-sm text-slate-500 space-y-1">
        <p>착용 횟수: <span className="text-slate-800 font-medium">{garment.wearCount}회</span></p>
        {garment.lastWornAt && (
          <p>마지막 착용: <span className="text-slate-800">{new Date(garment.lastWornAt).toLocaleDateString("ko-KR")}</span></p>
        )}
      </div>

      {garment.notes && (
        <p className="mt-4 text-sm text-slate-600 bg-slate-50 rounded-xl px-4 py-3">{garment.notes}</p>
      )}

      <div className="mt-6 flex gap-3">
        <Button variant="secondary" className="flex-1" onClick={() => router.push(`/garments/${id}/edit`)}>
          수정
        </Button>
      </div>
    </div>
  );
}
