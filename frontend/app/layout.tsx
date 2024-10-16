import type { Metadata } from "next";
import { Montserrat } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";

const montserrat = Montserrat({
  weight: ["100", "300", "400", "500", "700", "900"], // Add weights you need
  subsets: ["latin"], // Specify subsets if needed
});

export const metadata: Metadata = {
  title: "LifeStoryteller",
  description: "Capture and share your unique story with our digital album service, where you can easily create personalized albums filled with cherished memories and themes that resonate with you. Relive your moments anytime, anywhere!",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${ montserrat.className} antialiased`}>
      <Header />
        {children}
      </body>
    </html>
  );
}
