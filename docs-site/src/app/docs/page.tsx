"use client";

import Link from "next/link";
import { ArrowRight, Terminal, Book, Zap, Swords } from "lucide-react";
import { PixelCanvas } from "@/components/ui/pixel-canvas";

const cards = [
  { 
    title: "Installation", 
    href: "/docs/installation", 
    icon: Terminal, 
    desc: "Get up and running",
    colors: ["#1e3a5f", "#3b82f6", "#60a5fa"]
  },
  { 
    title: "Quickstart", 
    href: "/docs/quickstart", 
    icon: Zap, 
    desc: "Start your first session",
    colors: ["#422006", "#f59e0b", "#fbbf24"]
  },
  { 
    title: "Duel Engine", 
    href: "/docs/duel-engine", 
    icon: Swords, 
    desc: "The cognitive core",
    colors: ["#14532d", "#22c55e", "#4ade80"]
  },
  { 
    title: "CLI Commands", 
    href: "/docs/commands", 
    icon: Book, 
    desc: "Reference guide",
    colors: ["#581c87", "#a855f7", "#c084fc"]
  },
];

export default function DocsPage() {
  return (
    <div className="space-y-8 sm:space-y-12">
      <div className="space-y-3 sm:space-y-4">
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight">LearnLock Documentation</h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground">
          Everything you need to master adversarial learning with LearnLock.
        </p>
      </div>

      {/* Cards with PixelCanvas */}
      <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2">
        {cards.map((card) => (
          <Link key={card.href} href={card.href} className="block group">
            <div className="relative overflow-hidden border border-border rounded-xl p-4 sm:p-6 h-full bg-[#1f1f23] transition-colors hover:border-foreground/30">
              <PixelCanvas
                gap={6}
                speed={30}
                colors={card.colors}
                noFocus
              />
              <div className="relative z-10">
                <div className="flex items-center gap-2 sm:gap-3 mb-2 sm:mb-3">
                  <div className="p-1.5 sm:p-2 bg-primary/10 rounded-md text-primary group-hover:bg-primary/20 transition-colors">
                    <card.icon className="h-4 w-4 sm:h-5 sm:w-5" />
                  </div>
                  <h3 className="font-semibold text-base sm:text-lg">{card.title}</h3>
                </div>
                <p className="text-sm sm:text-base text-muted-foreground">{card.desc}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Quick Links */}
      <div className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">All Topics</h2>
        <div className="grid gap-2 sm:gap-3 grid-cols-1 sm:grid-cols-2">
          <Link href="/docs/installation" className="group p-3 sm:p-4 rounded-lg bg-[#1f1f23] border border-[#27272a] transition-all duration-300 hover:bg-[#252528]">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1 transition-colors duration-300 group-hover:text-white">Installation</h3>
            <p className="text-xs sm:text-sm text-muted-foreground transition-colors duration-300 group-hover:text-[#d4d4d8]">Get LearnLock running in under 5 minutes.</p>
          </Link>
          <Link href="/docs/quickstart" className="group p-3 sm:p-4 rounded-lg bg-[#1f1f23] border border-[#27272a] transition-all duration-300 hover:bg-[#252528]">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1 transition-colors duration-300 group-hover:text-white">Quickstart</h3>
            <p className="text-xs sm:text-sm text-muted-foreground transition-colors duration-300 group-hover:text-[#d4d4d8]">Add content and start studying in 2 minutes.</p>
          </Link>
          <Link href="/docs/adversarial-learning" className="group p-3 sm:p-4 rounded-lg bg-[#1f1f23] border border-[#27272a] transition-all duration-300 hover:bg-[#252528]">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1 transition-colors duration-300 group-hover:text-white">Adversarial Learning</h3>
            <p className="text-xs sm:text-sm text-muted-foreground transition-colors duration-300 group-hover:text-[#d4d4d8]">The philosophy behind the tool.</p>
          </Link>
          <Link href="/docs/socratic-dialogue" className="group p-3 sm:p-4 rounded-lg bg-[#1f1f23] border border-[#27272a] transition-all duration-300 hover:bg-[#252528]">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1 transition-colors duration-300 group-hover:text-white">Socratic Dialogue</h3>
            <p className="text-xs sm:text-sm text-muted-foreground transition-colors duration-300 group-hover:text-[#d4d4d8]">How LearnLock challenges your understanding.</p>
          </Link>
          <Link href="/docs/spaced-repetition" className="group p-3 sm:p-4 rounded-lg bg-[#1f1f23] border border-[#27272a] transition-all duration-300 hover:bg-[#252528]">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1 transition-colors duration-300 group-hover:text-white">Spaced Repetition</h3>
            <p className="text-xs sm:text-sm text-muted-foreground transition-colors duration-300 group-hover:text-[#d4d4d8]">The SM-2 algorithm that schedules reviews.</p>
          </Link>
          <Link href="/docs/duel-engine" className="group p-3 sm:p-4 rounded-lg bg-[#1f1f23] border border-[#27272a] transition-all duration-300 hover:bg-[#252528]">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1 transition-colors duration-300 group-hover:text-white">Duel Engine</h3>
            <p className="text-xs sm:text-sm text-muted-foreground transition-colors duration-300 group-hover:text-[#d4d4d8]">Belief modeling, claims, and interrogation.</p>
          </Link>
          <Link href="/docs/commands" className="group p-3 sm:p-4 rounded-lg bg-[#1f1f23] border border-[#27272a] transition-all duration-300 hover:bg-[#252528]">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1 transition-colors duration-300 group-hover:text-white">CLI Commands</h3>
            <p className="text-xs sm:text-sm text-muted-foreground transition-colors duration-300 group-hover:text-[#d4d4d8]">Complete reference for all commands.</p>
          </Link>
          <Link href="/docs/adding-content" className="group p-3 sm:p-4 rounded-lg bg-[#1f1f23] border border-[#27272a] transition-all duration-300 hover:bg-[#252528]">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1 transition-colors duration-300 group-hover:text-white">Adding Content</h3>
            <p className="text-xs sm:text-sm text-muted-foreground transition-colors duration-300 group-hover:text-[#d4d4d8]">YouTube, articles, PDFs, GitHub repos.</p>
          </Link>
          <Link href="/docs/study-sessions" className="group p-3 sm:p-4 rounded-lg bg-[#1f1f23] border border-[#27272a] transition-all duration-300 hover:bg-[#252528]">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1 transition-colors duration-300 group-hover:text-white">Study Sessions</h3>
            <p className="text-xs sm:text-sm text-muted-foreground transition-colors duration-300 group-hover:text-[#d4d4d8]">How to get the most out of study.</p>
          </Link>
          <Link href="/docs/ocr" className="group p-3 sm:p-4 rounded-lg bg-[#1f1f23] border border-[#27272a] transition-all duration-300 hover:bg-[#252528]">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1 transition-colors duration-300 group-hover:text-white">OCR Support</h3>
            <p className="text-xs sm:text-sm text-muted-foreground transition-colors duration-300 group-hover:text-[#d4d4d8]">Answer with handwritten notes.</p>
          </Link>
          <Link href="/docs/configuration" className="group p-3 sm:p-4 rounded-lg bg-[#1f1f23] border border-[#27272a] transition-all duration-300 hover:bg-[#252528]">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1 transition-colors duration-300 group-hover:text-white">Configuration</h3>
            <p className="text-xs sm:text-sm text-muted-foreground transition-colors duration-300 group-hover:text-[#d4d4d8]">All environment variables.</p>
          </Link>
        </div>
      </div>

      <div className="p-4 sm:p-6 rounded-lg border border-[#3f3f46] bg-[#1f1f23]">
        <h2 className="text-base sm:text-lg font-semibold mb-1.5 sm:mb-2">New to LearnLock?</h2>
        <p className="text-sm sm:text-base text-muted-foreground mb-3 sm:mb-4">
          Start with the installation guide, then follow the quickstart to add your first content.
        </p>
        <Link href="/docs/installation" className="inline-flex items-center gap-2 text-sm sm:text-base text-foreground hover:underline">
          Get started <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
