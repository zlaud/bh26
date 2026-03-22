import type { Metadata } from "next";
import { DM_Sans, Lora, DM_Mono } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";
import { DataProvider } from "@/context/DataContext";

const dmSans = DM_Sans({ subsets: ["latin"], variable: "--font-sans" });
const lora = Lora({ subsets: ["latin"], variable: "--font-serif" });
const dmMono = DM_Mono({
  subsets: ["latin"],
  weight: ["300", "400", "500"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "Canary",
  description: "Understand and adapt to food supply disruptions",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${dmSans.variable} ${lora.variable} ${dmMono.variable} min-h-screen`}
        style={{ backgroundColor: "#f7f4ef" }}
      >
        <DataProvider>
          <Header />
          {children}
        </DataProvider>
      </body>
    </html>
  );
}
