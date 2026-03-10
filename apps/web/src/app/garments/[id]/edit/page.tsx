"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/auth-context";
import { apiClient } from "@/lib/api-client";
import type { Garment, GarmentCategory, Season } from "@/types";

const CATEGORIES: { value: GarmentCategory; label: string }[] = [
  { value: "top", label: "상의" },
  { value: "bottom", label: "하의" },
  { value: "outer", label: "아우터" },
  { value: "dress", label: "원피스" },
  { value: "shoes", label: "신발" },
  { value: "bag", label: "가방" },
  { value: "accessory", label: "액세서리" },
  { value: "etc", label: "기타" },
];

const SEASONS: { value: Season; label: string }[] = [
  { value: "spring", label: "봄" },
  { value: "summer", label: "여름" },
  { value: "autumn", label: "가을" },
  { value: "winter", label: "겨울" },
];

export default function GarmentEditPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { token } = useAuth();

  const [garment, setGarment] = useState<Garment | null>(null);
  const [name, setName] = useState("");
  const [category, setCategory] = useState<GarmentCategory | "">("");
  const [seasons, setSeasons] = useState<Season[]>([]);
  const [styleTags, setStyleTags] = useState("");
  const [notes, setNotes] = useState("");
  const [brand, setBrand] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    apiClient
      .get<Garment>(`/garments/${id}`, { token })
      .then((g) => {
        setGarment(g);
        setName(g.name);
        setCategory((g.category as GarmentCategory) ?? "");
        setSeasons(g.seasons as Season[]);
        setStyleTags(g.styleTags.join(", "));
        setNotes(g.notes ?? "");
        setBrand(g.brand ?? "");
      })
      .catch(() => router.push("/closet"))
      .finally(() => setLoading(false));
  }, [id, token, router]);

  function toggleSeason(s: Season) {
    setSeasons((prev) =>
      prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]
    );
  }

  async function handleSave() {
    if (!token) return;
    setSaving(true);
    setError("");

    try {
      await apiClient.patch(
        `/garments/${id}`,
        {
          name,
          category: category || null,
          seasons,
          style_tags: styleTags.split(",").map((t) => t.trim()).filter(Boolean),
          notes: notes || null,
          brand: brand || null,
        },
        { token }
      );
      router.push(`/garments/${id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "저장에 실패했습니다.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="px-4 py-5 space-y-3">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-12 bg-slate-100 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (!garment) return null;

  return (
    <div className="px-4 py-5 max-w-md mx-auto">
      <button onClick={() => router.back()} className="text-sm text-slate-500 mb-4">← 뒤로</button>
      <h2 className="text-xl font-bold text-slate-900 mb-5">옷 정보 수정</h2>

      <div className="space-y-4">
        {/* 이름 */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">이름</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 bg-white"
          />
        </div>

        {/* 카테고리 */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">카테고리</label>
          <div className="flex flex-wrap gap-2">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.value}
                onClick={() => setCategory(cat.value)}
                className={`text-sm px-3 py-1.5 rounded-full border transition-colors ${
                  category === cat.value
                    ? "bg-slate-900 text-white border-slate-900"
                    : "bg-white text-slate-600 border-slate-200"
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* 계절 */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">계절</label>
          <div className="flex gap-2">
            {SEASONS.map((s) => (
              <button
                key={s.value}
                onClick={() => toggleSeason(s.value)}
                className={`text-sm px-3 py-1.5 rounded-full border transition-colors ${
                  seasons.includes(s.value)
                    ? "bg-blue-600 text-white border-blue-600"
                    : "bg-white text-slate-600 border-slate-200"
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {/* 브랜드 */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">브랜드 (선택)</label>
          <input
            value={brand}
            onChange={(e) => setBrand(e.target.value)}
            placeholder="예: 나이키"
            className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 bg-white"
          />
        </div>

        {/* 스타일 태그 */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">스타일 태그</label>
          <input
            value={styleTags}
            onChange={(e) => setStyleTags(e.target.value)}
            placeholder="쉼표로 구분 (예: 캐주얼, 미니멀)"
            className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 bg-white"
          />
        </div>

        {/* 메모 */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">메모 (선택)</label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            placeholder="구매처, 사이즈 등 자유롭게"
            className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 bg-white resize-none"
          />
        </div>

        {error && <p className="text-sm text-red-500">{error}</p>}

        <Button onClick={handleSave} loading={saving} className="w-full" size="lg">
          저장
        </Button>
      </div>
    </div>
  );
}
