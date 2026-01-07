import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "@/components/ui/Toast";

export const metadata: Metadata = {
  title: "Todo App - Phase II Hackathon",
  description: "Professional full-stack todo application with beautiful UI/UX",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
        <Toaster />
      </body>
    </html>
  );
}
