"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import type { User } from "@/types";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchMe = useCallback(async (t: string) => {
    try {
      const me = await apiClient.get<User>("/auth/me", { token: t });
      setUser(me);
      setToken(t);
    } catch {
      localStorage.removeItem("access_token");
      setUser(null);
      setToken(null);
    }
  }, []);

  useEffect(() => {
    const saved = localStorage.getItem("access_token");
    if (saved) {
      fetchMe(saved).finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, [fetchMe]);

  const login = useCallback(
    async (t: string) => {
      localStorage.setItem("access_token", t);
      await fetchMe(t);
    },
    [fetchMe]
  );

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    setUser(null);
    setToken(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
