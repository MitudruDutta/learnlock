"use client";

import Link from "next/link";
import { ArrowRight, Terminal, Book, Zap, Brain } from "lucide-react";

const cards = [
  { title: "Installation", href: "/docs/installation", icon: Terminal, desc: "Get up and running" },
  { title: "Quickstart", href: "/docs/quickstart", icon: Zap, desc: "Start your first session" },
  { title: "Adversarial Learning", href: "/docs/adversarial-learning", icon: Brain, desc: "Understand the methodology" },
  { title: "CLI Commands", href: "/docs/commands", icon: Book, desc: "Reference guide" },
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

      {/* Cards */}
      <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2">
        {cards.map((card) => (
          <Link key={card.href} href={card.href} className="block group">
            <div className="border border-border p-4 sm:p-6 rounded-xl hover:bg-muted/50 transition-colors h-full">
              <div className="flex items-center gap-2 sm:gap-3 mb-2 sm:mb-3">
                <div className="p-1.5 sm:p-2 bg-primary/10 rounded-md text-primary group-hover:bg-primary/20 transition-colors">
                    <card.icon className="h-4 w-4 sm:h-5 sm:w-5" />
                </div>
                <h3 className="font-semibold text-base sm:text-lg">{card.title}</h3>
              </div>
              <p className="text-sm sm:text-base text-muted-foreground">{card.desc}</p>
            </div>
          </Link>
        ))}
      </div>

      {/* Quick Links */}
      <div className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">All Topics</h2>
        <div className="grid gap-2 sm:gap-3 grid-cols-1 sm:grid-cols-2">
          <Link href="/docs/installation" className="group p-3 sm:p-4 rounded-lg border border-border/50 hover:border-foreground/30 transition-colors">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1">Installation</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">Get LearnLock running in under 5 minutes.</p>
          </Link>
          <Link href="/docs/quickstart" className="group p-3 sm:p-4 rounded-lg border border-border/50 hover:border-foreground/30 transition-colors">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1">Quickstart</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">Add content and start studying in 2 minutes.</p>
          </Link>
          <Link href="/docs/adversarial-learning" className="group p-3 sm:p-4 rounded-lg border border-border/50 hover:border-foreground/30 transition-colors">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1">Adversarial Learning</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">The philosophy behind the tool.</p>
          </Link>
          <Link href="/docs/socratic-dialogue" className="group p-3 sm:p-4 rounded-lg border border-border/50 hover:border-foreground/30 transition-colors">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1">Socratic Dialogue</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">How LearnLock challenges your understanding.</p>
          </Link>
          <Link href="/docs/spaced-repetition" className="group p-3 sm:p-4 rounded-lg border border-border/50 hover:border-foreground/30 transition-colors">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1">Spaced Repetition</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">The SM-2 algorithm that schedules reviews.</p>
          </Link>
          <Link href="/docs/commands" className="group p-3 sm:p-4 rounded-lg border border-border/50 hover:border-foreground/30 transition-colors">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1">CLI Commands</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">Complete reference for all commands.</p>
          </Link>
          <Link href="/docs/adding-content" className="group p-3 sm:p-4 rounded-lg border border-border/50 hover:border-foreground/30 transition-colors">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1">Adding Content</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">YouTube, articles, PDFs, GitHub repos.</p>
          </Link>
          <Link href="/docs/study-sessions" className="group p-3 sm:p-4 rounded-lg border border-border/50 hover:border-foreground/30 transition-colors">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1">Study Sessions</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">How to get the most out of study.</p>
          </Link>
          <Link href="/docs/ocr" className="group p-3 sm:p-4 rounded-lg border border-border/50 hover:border-foreground/30 transition-colors">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1">OCR Support</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">Answer with handwritten notes.</p>
          </Link>
          <Link href="/docs/configuration" className="group p-3 sm:p-4 rounded-lg border border-border/50 hover:border-foreground/30 transition-colors">
            <h3 className="font-medium text-sm sm:text-base mb-0.5 sm:mb-1">Configuration</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">All environment variables.</p>
          </Link>
        </div>
      </div>

      <div className="p-4 sm:p-6 rounded-lg border border-border/50 bg-card/50">
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