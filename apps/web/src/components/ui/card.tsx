import { type HTMLAttributes } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {}

export function Card({ className = "", children, ...props }: CardProps) {
  return (
    <div className={`bg-white rounded-2xl border border-slate-100 ${className}`} {...props}>
      {children}
    </div>
  );
}
