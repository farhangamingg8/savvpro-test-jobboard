import type { Metadata } from "next";
import { Header } from "@/components/Header";
import "./globals.css";

export const metadata: Metadata = {
  title: "JobBoard Pro Admin",
  description: "Manage jobs, candidates, and hiring analytics.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body><Header /><main>{children}</main><footer className="site-footer">JobBoard Pro · Hiring administration</footer></body>
    </html>
  );
}
