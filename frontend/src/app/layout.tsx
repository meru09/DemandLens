
import type { Metadata } from "next";
import {
  Inter,
  Space_Grotesk,
  JetBrains_Mono,
} from "next/font/google";

import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "DemandLens | Retail Intelligence",
  description:
    "Explore historical retail sales and evaluate product demand forecasts with DemandLens.",
};

export default function RootLayout({
  children,
}: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`
        ${inter.variable}
        ${spaceGrotesk.variable}
        ${jetbrainsMono.variable}
        h-full antialiased
      `}
    >
      <body className="min-h-full">{children}</body>
    </html>
  );
}
