import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] px-4 text-center">
      <h1 className="text-3xl font-bold text-slate-900 mb-3">ClosetIQ</h1>
      <p className="text-slate-500 mb-8 max-w-xs">
        AI가 내 옷장을 정리하고, 오늘의 코디를 추천해드립니다.
      </p>
      <Link
        href="/closet"
        className="bg-slate-900 text-white px-6 py-3 rounded-xl text-sm font-medium"
      >
        옷장 보기
      </Link>
    </div>
  );
}
