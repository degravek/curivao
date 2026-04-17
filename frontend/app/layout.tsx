import type { Metadata } from "next";
import { Poppins, Dancing_Script } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

const poppins = Poppins({
  weight: ["300", "400", "500", "600", "700"],
  subsets: ["latin"],
});

export const dancingScript = Dancing_Script({
  weight: ["700"],
  subsets: ["latin"],
  variable: "--font-dancing",
});

export const metadata: Metadata = {
  title: "Curivao — Discover Your Next Room",
  description:
    "AI-curated interior design rooms with shoppable furniture from top retailers.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${poppins.className} ${dancingScript.variable} h-full`}>
      <head>
        <meta name="impact-site-verification" value="081190c2-4b2f-4cdf-ad77-bdefaec5ad03" />
      </head>
      <body className="min-h-full flex flex-col antialiased">
        <Navbar />
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
