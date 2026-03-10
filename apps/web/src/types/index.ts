export interface User {
  id: string;
  email: string;
  displayName: string;
  createdAt: string;
}

export type ProcessingStatus = "pending" | "processing" | "done" | "failed";

export type GarmentCategory =
  | "top"
  | "bottom"
  | "outer"
  | "dress"
  | "shoes"
  | "bag"
  | "accessory"
  | "etc";

export type Season = "spring" | "summer" | "autumn" | "winter";

export interface Garment {
  id: string;
  userId: string;
  name: string;
  originalImageUrl: string;
  cutoutImageUrl: string | null;
  thumbnailUrl: string | null;
  processingStatus: ProcessingStatus;
  category: GarmentCategory | null;
  subcategory: string | null;
  brand: string | null;
  dominantColors: string[];
  seasons: Season[];
  styleTags: string[];
  notes: string | null;
  wearCount: number;
  lastWornAt: string | null;
  isArchived: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  meta?: {
    total: number;
    page: number;
    limit: number;
  };
}
