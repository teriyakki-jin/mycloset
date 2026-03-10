"use client";

import { useState } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/contexts/auth-context";
import { apiClient } from "@/lib/api-client";
import type { Garment } from "@/types";

const OCCASIONS = [
  { value: "daily", label: "데일리" },
  { value: "work", label: "출근" },
  { value: "date", label: "데이트" },
  { value: "party", label: "모임" },
  { value: "exercise", label: "운동" },
] as const;

interface OutfitSet {
  top: Garment | null;
  bottom: Garment | null;
  outer: Garment | null;
  score: number;
  explanation: string;
}

interface RecommendResponse {
  outfits: OutfitSet[];
}

function GarmentThumb({ garment }: { garment: Garment }) {
  const url = garment.thumbnailUrl ?? garment.cutoutImageUrl ?? garment.originalImageUrl;
  return (
    <div className="relative aspect-[3/4] rounded-xl overflow-hidden bg-slate-100 flex-1">
      <Image src={url} alt={garment.name} fill className="object-cover" sizes="120px" />
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 px-2 py-1.5">
        <p className="text-white text-xs truncate">{garment.name}</p>
      </div>
    </div>
  );
}

function OutfitCard({ outfit, index }: { outfit: OutfitSet; index: number }) {
  const items = [outfit.top, outfit.outer, outfit.bottom].filter(Boolean) as Garment[];
  return (
    <Card className="p-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-xs font-bold bg-slate-900 text-white w-5 h-5 rounded-full flex items-center justify-center">
          {index + 1}
        </span>
        <p className="text-xs text-slate-500 flex-1 leading-relaxed">{outfit.explanation}</p>
      </div>
      <div className="flex gap-2">
        {items.map((g) => (
          <GarmentThumb key={g.id} garment={g} />
        ))}
        {items.length === 0 && (
          <p className="text-sm text-slate-400 py-4 w-full text-center">코디를 구성할 옷이 부족합니다.</p>
        )}
      </div>
    </Card>
  );
}

export default function OutfitPage() {
  const { token } = useAuth();
  const [occasion, setOccasion] = useState<string>("daily");
  const [temp, setTemp] = useState<string>("");
  const [outfits, setOutfits] = useState<OutfitSet[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleRecommend() {
    if (!token) { setError("로그인이 필요합니다."); return; }
    setLoading(true);
    setError("");

    try {
      const body: Record<string, unknown> = { occasion };
      if (temp) body.temp_celsius = parseFloat(temp);

      const data = await apiClient.post<RecommendResponse>("/recommendations/outfit", body, { token });
      setOutfits(data.outfits);
    } catch (err) {
      setError(err instanceof Error ? err.message : "추천 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="px-4 py-5 max-w-md mx-auto">
      <h2 className="text-xl font-bold text-slate-900 mb-5">코디 추천</h2>

      {/* 상황 선택 */}
      <div className="mb-4">
        <p className="text-sm font-medium text-slate-700 mb-2">오늘의 상황</p>
        <div className="flex gap-2 flex-wrap">
          {OCCASIONS.map((o) => (
            <button
              key={o.value}
              onClick={() => setOccasion(o.value)}
              className={`text-sm px-4 py-2 rounded-full border transition-colors ${
                occasion === o.value
                  ? "bg-slate-900 text-white border-slate-900"
                  : "bg-white text-slate-600 border-slate-200 hover:border-slate-400"
              }`}
            >
              {o.label}
            </button>
          ))}
        </div>
      </div>

      {/* 온도 입력 */}
      <div className="mb-5">
        <p className="text-sm font-medium text-slate-700 mb-2">현재 기온 (선택)</p>
        <div className="flex items-center gap-2">
          <input
            type="number"
            value={temp}
            onChange={(e) => setTemp(e.target.value)}
            placeholder="예: 18"
            className="w-28 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 bg-white"
          />
          <span className="text-sm text-slate-400">°C</span>
        </div>
      </div>

      <Button onClick={handleRecommend} loading={loading} className="w-full mb-6" size="lg">
        코디 추천 받기
      </Button>

      {error && <p className="text-sm text-red-500 mb-4">{error}</p>}

      {outfits.length > 0 && (
        <div className="space-y-4">
          {outfits.map((outfit, i) => (
            <OutfitCard key={i} outfit={outfit} index={i} />
          ))}
        </div>
      )}

      {outfits.length === 0 && !loading && (
        <div className="text-center py-10 text-slate-400 text-sm space-y-1">
          <p>위 버튼을 눌러 오늘의 코디를 추천받아보세요.</p>
          <p className="text-xs text-slate-300">상의·하의가 각 1개 이상 있어야 코디를 구성할 수 있어요.</p>
        </div>
      )}
    </div>
  );
}
