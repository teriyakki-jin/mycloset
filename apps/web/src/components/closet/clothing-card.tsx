import Image from "next/image";
import Link from "next/link";
import type { Garment } from "@/types";

interface ClothingCardProps {
  garment: Garment;
}

const STATUS_LABEL: Record<string, string> = {
  pending: "대기",
  processing: "처리 중",
  done: "",
  failed: "실패",
};

export function ClothingCard({ garment }: ClothingCardProps) {
  const imageUrl = garment.cutoutImageUrl ?? garment.originalImageUrl ?? "";
  const isProcessing = garment.processingStatus === "pending" || garment.processingStatus === "processing";

  return (
    <Link href={`/garments/${garment.id}`} className="block group">
      <div className="relative aspect-[3/4] rounded-xl overflow-hidden bg-slate-100">
        <Image
          src={imageUrl}
          alt={garment.name}
          fill
          className="object-cover group-hover:scale-105 transition-transform duration-300"
          sizes="(max-width: 640px) 50vw, 33vw"
        />
        {isProcessing && (
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
            <span className="text-white text-xs font-medium bg-black/50 px-2 py-1 rounded-full">
              {STATUS_LABEL[garment.processingStatus]}
            </span>
          </div>
        )}
        {garment.processingStatus === "failed" && (
          <div className="absolute inset-0 bg-red-500/20 flex items-end p-2">
            <span className="text-red-600 text-xs font-medium">처리 실패</span>
          </div>
        )}
      </div>
      <div className="mt-1.5 px-0.5">
        <p className="text-sm font-medium text-slate-800 truncate">{garment.name}</p>
        {garment.category && (
          <p className="text-xs text-slate-400 mt-0.5">{garment.category}</p>
        )}
      </div>
    </Link>
  );
}
