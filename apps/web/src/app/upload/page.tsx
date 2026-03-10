"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { API_URL } from "@/lib/constants";

type UploadState = "idle" | "uploading" | "done" | "error";

export default function UploadPage() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<UploadState>("idle");
  const [errorMsg, setErrorMsg] = useState("");

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0];
    if (!selected) return;
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setState("idle");
  }

  async function handleUpload() {
    if (!file) return;

    const token = localStorage.getItem("access_token");
    if (!token) {
      setErrorMsg("로그인이 필요합니다.");
      setState("error");
      return;
    }

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

  return (
    <div className="px-4 py-5 max-w-md mx-auto">
      <h2 className="text-xl font-bold text-slate-900 mb-6">옷 등록</h2>

      {/* 이미지 선택 영역 */}
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

      {state === "error" && (
        <p className="mt-3 text-sm text-red-500">{errorMsg}</p>
      )}

      {state === "done" && (
        <p className="mt-3 text-sm text-green-600 font-medium">업로드 완료! AI가 처리 중입니다.</p>
      )}

      <div className="mt-5 flex gap-3">
        {preview && (
          <Button
            variant="secondary"
            className="flex-1"
            onClick={() => {
              setPreview(null);
              setFile(null);
              setState("idle");
            }}
          >
            다시 선택
          </Button>
        )}
        <Button
          className="flex-1"
          disabled={!file || state === "uploading" || state === "done"}
          loading={state === "uploading"}
          onClick={handleUpload}
        >
          {state === "done" ? "완료" : "업로드"}
        </Button>
      </div>

      <p className="mt-4 text-xs text-slate-400 text-center">
        AI가 배경을 제거하고 자동으로 태그를 붙여드립니다.
      </p>
    </div>
  );
}
