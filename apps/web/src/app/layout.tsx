import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Header } from "@/components/layout/header";
import { BottomNav } from "@/components/layout/bottom-nav";
import { AuthProvider } from "@/contexts/auth-context";
import { APP_NAME } from "@/lib/constants";

export const metadata: Metadata = {
  title: APP_NAME,
  description: "AI 기반 옷장 관리 서비스",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: APP_NAME,
  },
};

export const viewport: Viewport = {
  themeColor: "#0f172a",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="bg-slate-50 min-h-screen">
        <AuthProvider>
          <Header />
          <main className="pb-20">{children}</main>
          <BottomNav />
        </AuthProvider>
      </body>
    </html>
  );
}
