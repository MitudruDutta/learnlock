import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/blocks/navbar";

export const metadata: Metadata = {
  title: {
    default: "LearnLock - The App That Argues With You",
    template: "%s | LearnLock",
  },
  description: "Stop consuming. Start retaining. A CLI tool that uses adversarial Socratic dialogue to expose gaps in your understanding.",
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background font-sans antialiased">
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}