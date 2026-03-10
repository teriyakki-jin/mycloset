"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/auth-context";
import { apiClient } from "@/lib/api-client";
import { API_URL } from "@/lib/constants";
import type { Garment, GarmentCategory, Season } from "@/types";

const SEASON_LABEL: Record<Season, string> = {
  spring: "봄", summer: "여름", autumn: "가을", winter: "겨울",
};

const CATEGORY_LABEL: Record<GarmentCategory, string> = {
  top: "상의", bottom: "하의", outer: "아우터", dress: "원피스",
  shoes: "신발", bag: "가방", accessory: "액세서리", etc: "기타",
};

export default function GarmentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { token } = useAuth();
  const [garment, setGarment] = useState<Garment | null>(null);
  const [loading, setLoading] = useState(true);
  const [logging, setLogging] = useState(false);
  const [logDone, setLogDone] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // 가상 피팅 상태
  const personInputRef = useRef<HTMLInputElement>(null);
  const [personPreview, setPersonPreview] = useState<string | null>(null);
  const [personUrl, setPersonUrl] = useState<string | null>(null);
  const [tryonLoading, setTryonLoading] = useState(false);
  const [tryonResult, setTryonResult] = useState<string | null>(null);
  const [tryonError, setTryonError] = useState("");

  useEffect(() => {
    if (!token) return;
    apiClient
      .get<Garment>(`/garments/${id}`, { token })
      .then(setGarment)
      .catch(() => router.push("/closet"))
      .finally(() => setLoading(false));
  }, [id, token, router]);

  async function handleDelete() {
    if (!token || !garment) return;
    if (!confirm(`"${garment.name}"을(를) 삭제할까요?`)) return;
    setDeleting(true);
    try {
      await apiClient.delete(`/garments/${garment.id}`, { token });
      router.push("/closet");
    } catch {
      alert("삭제에 실패했습니다.");
      setDeleting(false);
    }
  }

  async function handleWearLog() {
    if (!token || !garment) return;
    setLogging(true);
    try {
      await apiClient.post(
        "/wear-logs",
        { garment_id: garment.id, worn_at: new Date().toISOString() },
        { token }
      );
      setLogDone(true);
      setGarment((prev) => prev ? { ...prev, wearCount: prev.wearCount + 1 } : prev);
    } catch {
    } finally {
      setLogging(false);
    }
  }

  async function handlePersonSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file || !token) return;

    setPersonPreview(URL.createObjectURL(file));
    setTryonResult(null);
    setTryonError("");

    // 서버에 업로드해서 URL 받기
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_URL}/tryon/upload-person`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });
    if (res.ok) {
      const data = await res.json();
      setPersonUrl(data.url);
    }
  }

  async function handleTryon() {
    if (!token || !garment || !personUrl) return;
    setTryonLoading(true);
    setTryonResult(null);
    setTryonError("");
    try {
      const data = await apiClient.post<{ resultUrl: string }>(
        "/tryon",
        { garment_id: garment.id, person_image_url: personUrl },
        { token }
      );
      setTryonResult(data.resultUrl);
    } catch (err) {
      setTryonError(err instanceof Error ? err.message : "가상 피팅 처리 중 오류가 발생했습니다.");
    } finally {
      setTryonLoading(false);
    }
  }

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

  const imageUrl = garment.cutoutImageUrl ?? garment.originalImageUrl ?? "";

  return (
    <div className="px-4 py-5 max-w-md mx-auto">
      <button onClick={() => router.back()} className="text-sm text-slate-500 mb-4">← 뒤로</button>

      <div className="relative aspect-[3/4] rounded-2xl overflow-hidden bg-slate-100 mb-5">
        <Image src={imageUrl} alt={garment.name} fill className="object-cover" />
        {garment.processingStatus === "processing" && (
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
            <p className="text-white text-sm font-medium">AI 처리 중...</p>
          </div>
        )}
      </div>

      <h2 className="text-xl font-bold text-slate-900 mb-1">{garment.name}</h2>

      <div className="flex flex-wrap gap-1.5 mt-3">
        {garment.category && (
          <span className="text-xs bg-slate-100 text-slate-700 px-2.5 py-1 rounded-full">
            {CATEGORY_LABEL[garment.category as GarmentCategory] ?? garment.category}
          </span>
        )}
        {(garment.seasons ?? []).map((s) => (
          <span key={s} className="text-xs bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full">
            {SEASON_LABEL[s as Season] ?? s}
          </span>
        ))}
        {(garment.styleTags ?? []).map((tag) => (
          <span key={tag} className="text-xs bg-slate-50 text-slate-500 px-2.5 py-1 rounded-full border border-slate-200">
            #{tag}
          </span>
        ))}
      </div>

      {(garment.dominantColors ?? []).length > 0 && (
        <div className="mt-4">
          <p className="text-xs text-slate-400 mb-1.5">대표 색상</p>
          <div className="flex gap-2">
            {(garment.dominantColors ?? []).map((color) => (
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
        {garment.brand && <p>브랜드: <span className="text-slate-800">{garment.brand}</span></p>}
      </div>

      {garment.notes && (
        <p className="mt-4 text-sm text-slate-600 bg-slate-50 rounded-xl px-4 py-3">{garment.notes}</p>
      )}

      {/* 가상 피팅 섹션 */}
      <div className="mt-6 border border-slate-200 rounded-2xl p-4">
        <p className="text-sm font-semibold text-slate-800 mb-3">가상 피팅</p>
        <p className="text-xs text-slate-400 mb-3">내 사진을 올리면 AI가 이 옷을 입혀드립니다. (30~60초 소요)</p>

        <input
          ref={personInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          onChange={handlePersonSelect}
        />

        <button
          onClick={() => personInputRef.current?.click()}
          className="w-full border-2 border-dashed border-slate-200 rounded-xl py-4 flex flex-col items-center gap-1 hover:border-slate-400 transition-colors overflow-hidden relative"
        >
          {personPreview ? (
            <div className="relative w-full aspect-[3/4]">
              <Image src={personPreview} alt="내 사진" fill className="object-cover rounded-lg" />
            </div>
          ) : (
            <>
              <span className="text-2xl">🧍</span>
              <p className="text-xs text-slate-400">내 사진 선택 (전신 또는 상반신)</p>
            </>
          )}
        </button>

        {tryonError && (
          <p className="mt-2 text-xs text-red-500">{tryonError}</p>
        )}

        <Button
          className="w-full mt-3"
          disabled={!personUrl || tryonLoading}
          loading={tryonLoading}
          onClick={handleTryon}
        >
          {tryonLoading ? "AI 피팅 중... (최대 1분)" : "입어보기"}
        </Button>

        {tryonResult && (
          <div className="mt-4">
            <p className="text-xs text-slate-400 mb-2">피팅 결과</p>
            <div className="relative aspect-[3/4] rounded-xl overflow-hidden bg-slate-100">
              <Image src={tryonResult} alt="피팅 결과" fill className="object-cover" />
            </div>
          </div>
        )}
      </div>

      <div className="mt-6 flex gap-3">
        <Button
          variant="secondary"
          className="flex-1"
          onClick={() => router.push(`/garments/${id}/edit`)}
        >
          수정
        </Button>
        <Button
          className="flex-1"
          variant={logDone ? "secondary" : "primary"}
          loading={logging}
          onClick={handleWearLog}
          disabled={logDone}
        >
          {logDone ? "기록 완료 ✓" : "오늘 입었어요"}
        </Button>
      </div>

      <div className="mt-3">
        <Button
          variant="secondary"
          className="w-full text-red-500 hover:text-red-600"
          loading={deleting}
          onClick={handleDelete}
        >
          삭제
        </Button>
      </div>
    </div>
  );
}
