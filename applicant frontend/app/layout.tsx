import type { Metadata } from "next";
import { Header } from "@/components/Header";
import "./globals.css";

export const metadata: Metadata = { title: "JobBoard Pro Careers", description: "Find and apply for your next role." };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><Header /><main>{children}</main><footer className="site-footer">JobBoard Pro · Built for thoughtful hiring</footer></body></html>;
}

