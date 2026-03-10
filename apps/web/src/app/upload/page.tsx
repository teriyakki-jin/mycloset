"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { API_URL } from "@/lib/constants";
import { apiClient } from "@/lib/api-client";
import { useAuth } from "@/contexts/auth-context";

type Tab = "photo" | "url";
type UploadState = "idle" | "uploading" | "done" | "error";

export default function UploadPage() {
  const router = useRouter();
  const { token } = useAuth();
  const inputRef = useRef<HTMLInputElement>(null);

  const [tab, setTab] = useState<Tab>("photo");

  // 사진 업로드
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);

  // URL 임포트
  const [url, setUrl] = useState("");
  const [urlPreview, setUrlPreview] = useState<{ name: string; imageUrl: string } | null>(null);
  const [fetchingUrl, setFetchingUrl] = useState(false);

  const [state, setState] = useState<UploadState>("idle");
  const [errorMsg, setErrorMsg] = useState("");

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0];
    if (!selected) return;
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setState("idle");
  }

  async function handlePhotoUpload() {
    if (!file || !token) return;
    setState("uploading");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch(`${API_URL}/garments/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "업로드 실패" }));
        throw new Error(err.detail ?? "업로드 실패");
      }
      setState("done");
      setTimeout(() => router.push("/closet"), 800);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "업로드 중 오류가 발생했습니다.");
      setState("error");
    }
  }

  async function handleFetchUrl() {
    if (!url.trim()) {
      setErrorMsg("URL을 입력해주세요.");
      setState("error");
      return;
    }
    if (!token) {
      setErrorMsg("로그인이 필요합니다.");
      setState("error");
      return;
    }
    setFetchingUrl(true);
    setErrorMsg("");
    setState("idle");
    try {
      await apiClient.post(
        "/garments/import-url",
        { url: url.trim() },
        { token }
      );
      setState("done");
      setTimeout(() => router.push("/closet"), 800);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "URL에서 상품 정보를 가져올 수 없습니다.";
      // API 에러 JSON 파싱 시도
      try {
        const parsed = JSON.parse(msg);
        setErrorMsg(parsed.detail ?? msg);
      } catch {
        setErrorMsg(msg);
      }
      setState("error");
    } finally {
      setFetchingUrl(false);
    }
  }

  function switchTab(t: Tab) {
    setTab(t);
    setState("idle");
    setErrorMsg("");
  }

  return (
    <div className="px-4 py-5 max-w-md mx-auto">
      <h2 className="text-xl font-bold text-slate-900 mb-5">옷 등록</h2>

      {/* 탭 */}
      <div className="flex rounded-xl bg-slate-100 p-1 mb-5">
        <button
          className={`flex-1 py-2 text-sm font-medium rounded-lg transition-colors ${tab === "photo" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500"}`}
          onClick={() => switchTab("photo")}
        >
          📷 사진 업로드
        </button>
        <button
          className={`flex-1 py-2 text-sm font-medium rounded-lg transition-colors ${tab === "url" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500"}`}
          onClick={() => switchTab("url")}
        >
          🔗 URL로 가져오기
        </button>
      </div>

      {/* 사진 업로드 탭 */}
      {tab === "photo" && (
        <>
          <button
            onClick={() => inputRef.current?.click()}
            className="w-full aspect-[3/4] rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 flex flex-col items-center justify-center gap-3 hover:border-slate-400 transition-colors overflow-hidden relative"
          >
            {preview ? (
              <Image src={preview} alt="미리보기" fill className="object-cover rounded-2xl" />
            ) : (
              <>
                <span className="text-4xl">📷</span>
                <p className="text-sm text-slate-400">사진을 선택하세요</p>
                <p className="text-xs text-slate-300">JPG, PNG, WEBP · 최대 20MB</p>
              </>
            )}
          </button>
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={handleFileChange}
          />
          {state === "error" && <p className="mt-3 text-sm text-red-500">{errorMsg}</p>}
          {state === "done" && <p className="mt-3 text-sm text-green-600 font-medium">업로드 완료! AI가 처리 중입니다.</p>}
          <div className="mt-5 flex gap-3">
            {preview && (
              <Button variant="secondary" className="flex-1" onClick={() => { setPreview(null); setFile(null); setState("idle"); }}>
                다시 선택
              </Button>
            )}
            <Button
              className="flex-1"
              disabled={!file || state === "uploading" || state === "done"}
              loading={state === "uploading"}
              onClick={handlePhotoUpload}
            >
              {state === "done" ? "완료" : "업로드"}
            </Button>
          </div>
        </>
      )}

      {/* URL 임포트 탭 */}
      {tab === "url" && (
        <>
          <div className="space-y-3">
            <p className="text-sm text-slate-500">
              쇼핑몰 상품 페이지 URL을 붙여넣으면 이미지와 이름을 자동으로 가져옵니다.
            </p>
            <p className="text-xs text-slate-400">
              지원: 무신사 · 29CM · 지그재그 · 에이블리 · 기타 og:image 지원 사이트
            </p>
            <input
              type="url"
              value={url}
              onChange={(e) => { setUrl(e.target.value); setState("idle"); setErrorMsg(""); }}
              placeholder="https://www.musinsa.com/products/..."
              className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 bg-white"
            />
          </div>

          {state === "error" && <p className="mt-3 text-sm text-red-500">{errorMsg}</p>}
          {state === "done" && <p className="mt-3 text-sm text-green-600 font-medium">등록 완료! AI가 처리 중입니다.</p>}

          <div className="mt-5">
            <Button
              className="w-full"
              disabled={!url.trim() || fetchingUrl || state === "done"}
              loading={fetchingUrl}
              onClick={handleFetchUrl}
            >
              {state === "done" ? "완료" : "가져오기"}
            </Button>
          </div>
        </>
      )}

      <p className="mt-4 text-xs text-slate-400 text-center">
        AI가 배경을 제거하고 자동으로 태그를 붙여드립니다.
      </p>
    </div>
  );
}
