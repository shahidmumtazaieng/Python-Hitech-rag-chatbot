import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hitech Steel Industries - AI Assistant",
  description: "AI-powered chatbot for Hitech Steel Industries",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
