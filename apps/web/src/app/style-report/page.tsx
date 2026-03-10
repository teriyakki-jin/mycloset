"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/contexts/auth-context";
import { apiClient } from "@/lib/api-client";

interface StyleReport {
  totalGarments: number;
  topColors: { color: string; count: number }[];
  categoryDistribution: { category: string; count: number; pct: number }[];
  formalityAvg: number | null;
  casualRatio: number;
  formalRatio: number;
  unworn60dCount: number;
  topStyleTags: string[];
  missingCategories: string[];
  totalWearLogs: number;
  mostWornGarment: { name: string; wearCount: number } | null;
  summary: string;
}

function StatCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <Card className="p-4 flex flex-col gap-1">
      <p className="text-xs text-slate-400">{label}</p>
      <p className="text-2xl font-bold text-slate-900">{value}</p>
      {sub && <p className="text-xs text-slate-400">{sub}</p>}
    </Card>
  );
}

function BarChart({ items }: { items: { category: string; pct: number; count: number }[] }) {
  return (
    <div className="space-y-2.5">
      {items.map((item) => (
        <div key={item.category}>
          <div className="flex justify-between text-xs text-slate-600 mb-1">
            <span>{item.category}</span>
            <span>{item.count}개 ({Math.round(item.pct * 100)}%)</span>
          </div>
          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-slate-700 rounded-full transition-all duration-500"
              style={{ width: `${item.pct * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function StyleReportPage() {
  const { token } = useAuth();
  const [report, setReport] = useState<StyleReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) { setLoading(false); return; }
    apiClient
      .get<StyleReport>("/style/report", { token })
      .then(setReport)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return (
      <div className="px-4 py-5 space-y-3">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-24 bg-slate-100 rounded-2xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (!report) {
    return (
      <div className="px-4 py-10 text-center text-slate-400 text-sm">
        로그인 후 스타일 분석을 확인할 수 있습니다.
      </div>
    );
  }

  const formalityLabel =
    report.formalityAvg === null
      ? "-"
      : report.formalityAvg < 0.35
      ? "캐주얼"
      : report.formalityAvg > 0.65
      ? "포멀"
      : "믹스";

  return (
    <div className="px-4 py-5 max-w-md mx-auto space-y-5">
      <h2 className="text-xl font-bold text-slate-900">스타일 리포트</h2>

      {/* 요약 */}
      <Card className="p-4 bg-slate-900 text-white">
        <p className="text-sm leading-relaxed">{report.summary}</p>
      </Card>

      {/* 주요 지표 */}
      <div className="grid grid-cols-2 gap-3">
        <StatCard label="보유 아이템" value={report.totalGarments} sub="개" />
        <StatCard label="총 착용 기록" value={report.totalWearLogs} sub="회" />
        <StatCard label="미착용 (60일)" value={report.unworn60dCount} sub="개" />
        <StatCard label="스타일 성향" value={formalityLabel} />
      </div>

      {/* 색상 팔레트 */}
      {report.topColors.length > 0 && (
        <Card className="p-4">
          <p className="text-sm font-semibold text-slate-800 mb-3">대표 색상</p>
          <div className="flex gap-3 flex-wrap">
            {report.topColors.map((c) => (
              <div key={c.color} className="flex flex-col items-center gap-1">
                <div
                  className="w-10 h-10 rounded-full border border-slate-200 shadow-sm"
                  style={{ backgroundColor: c.color }}
                />
                <span className="text-xs text-slate-400">{c.count}개</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* 카테고리 분포 */}
      {report.categoryDistribution.length > 0 && (
        <Card className="p-4">
          <p className="text-sm font-semibold text-slate-800 mb-3">카테고리 분포</p>
          <BarChart items={report.categoryDistribution} />
        </Card>
      )}

      {/* 스타일 태그 */}
      {report.topStyleTags.length > 0 && (
        <Card className="p-4">
          <p className="text-sm font-semibold text-slate-800 mb-3">주요 스타일 키워드</p>
          <div className="flex flex-wrap gap-2">
            {report.topStyleTags.map((tag) => (
              <span key={tag} className="text-sm bg-slate-100 text-slate-700 px-3 py-1 rounded-full">
                #{tag}
              </span>
            ))}
          </div>
        </Card>
      )}

      {/* 최다 착용 */}
      {report.mostWornGarment && (
        <Card className="p-4">
          <p className="text-sm font-semibold text-slate-800 mb-1">가장 많이 입은 옷</p>
          <p className="text-slate-700">{report.mostWornGarment.name}</p>
          <p className="text-xs text-slate-400 mt-0.5">{report.mostWornGarment.wearCount}회 착용</p>
        </Card>
      )}

      {/* 보완 추천 */}
      {report.missingCategories.length > 0 && (
        <Card className="p-4">
          <p className="text-sm font-semibold text-slate-800 mb-2">보완이 필요한 아이템</p>
          <div className="flex flex-wrap gap-2">
            {report.missingCategories.map((cat) => (
              <span key={cat} className="text-sm border border-dashed border-slate-300 text-slate-500 px-3 py-1 rounded-full">
                {cat} 추가하기
              </span>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
