"use client";

import { HeroSection } from "@/components/blocks/hero-section";
import { Terminal, ArrowRight } from "lucide-react";
import Link from "next/link";
import { InfiniteMovingCards } from "@/components/ui/infinite-moving-cards";

const features = [
  {
    quote: "The engine doesn't just grade you—it models your mental state. Infers what you believe, detects contradictions in real-time, tracks belief trajectory across turns.",
    name: "Belief Tracking",
    title: "Cognitive Modeling",
  },
  {
    quote: "Three turns. Graded harshness. Turn 1 is forgiving. Turn 2 flags omissions. Turn 3 surfaces everything. No mercy for vagueness.",
    name: "Socratic Attack",
    title: "Adversarial Dialogue",
  },
  {
    quote: "Three-pass filtering ensures fair interrogation. Rejects tautologies, filters blurry truths like 'handles X'. Only sharp, falsifiable claims survive.",
    name: "Claim Verification",
    title: "Quality Control",
  },
];

const features2 = [
  {
    quote: "The algorithm that powers Anki, built in. Reviews timed to interrupt forgetting. Intervals adapt to your performance. Mastery tracked per concept.",
    name: "SM-2 Scheduling",
    title: "Spaced Repetition",
  },
  {
    quote: "Point it at anything. YouTube videos with timestamps, articles, PDFs, GitHub repos. Extracts 8-12 atomic concepts per source automatically.",
    name: "Multi-Source Ingestion",
    title: "Content Extraction",
  },
  {
    quote: "Built for developers who live in the CLI. All data stored locally in SQLite. Zero distractions, keyboard-driven. Rich HUD with live engine state.",
    name: "Terminal Native",
    title: "Developer Experience",
  },
];

export default function Home() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-3.5rem)] bg-[#18181b]">
      <HeroSection />

      {/* Features Section - Infinite Moving Cards */}
      <section className="relative py-24 md:py-32 overflow-hidden">
        <div className="container mx-auto px-4 relative">
          <div className="mx-auto flex max-w-3xl flex-col items-center space-y-4 text-center mb-12">
            <span className="text-sm font-medium text-[#a1a1aa] uppercase tracking-wider">Why LearnLock</span>
            <h2 className="font-bold text-3xl leading-[1.1] sm:text-4xl md:text-5xl tracking-tight">
              Learning that <span className="text-green-500">actually sticks.</span>
            </h2>
            <p className="max-w-[85%] leading-normal text-[#a1a1aa] sm:text-lg sm:leading-7">
              Most tools test recall. LearnLock tests understanding. It models what you believe, finds where you&apos;re wrong, and won&apos;t stop until you fix it.
            </p>
          </div>
        </div>
        
        <InfiniteMovingCards
          items={features}
          direction="left"
          speed="slow"
          className="mb-6"
        />
        <InfiniteMovingCards
          items={features2}
          direction="right"
          speed="slow"
        />
      </section>

      {/* How It Works Section */}
      <section className="relative py-24 md:py-32 bg-[#1f1f23]/50">
        <div className="container mx-auto px-4">
          <div className="mx-auto flex max-w-3xl flex-col items-center space-y-4 text-center mb-16">
            <span className="text-sm font-medium text-[#a1a1aa] uppercase tracking-wider">The Duel</span>
            <h2 className="font-bold text-3xl leading-[1.1] sm:text-4xl md:text-5xl tracking-tight">
              You explain. <span className="text-green-500">It attacks.</span>
            </h2>
          </div>
          
          <div className="mx-auto max-w-4xl">
            <div className="grid gap-8 md:grid-cols-3">
              <div className="relative flex flex-col items-center text-center p-6">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#27272a] mb-4 border border-[#3f3f46]">
                  <span className="text-2xl font-bold text-green-500">1</span>
                </div>
                <h3 className="font-bold text-lg mb-2">Ingest</h3>
                <p className="text-sm text-[#a1a1aa]">Feed it a YouTube video, article, PDF, or GitHub repo. The LLM extracts 8-12 atomic concepts with falsifiable claims.</p>
              </div>
              
              <div className="relative flex flex-col items-center text-center p-6">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#27272a] mb-4 border border-[#3f3f46]">
                  <span className="text-2xl font-bold text-green-500">2</span>
                </div>
                <h3 className="font-bold text-lg mb-2">Duel</h3>
                <p className="text-sm text-[#a1a1aa]">Explain the concept. The engine infers your belief, compares it to ground truth, and generates targeted attacks on your weakest points.</p>
              </div>
              
              <div className="relative flex flex-col items-center text-center p-6">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#27272a] mb-4 border border-[#3f3f46]">
                  <span className="text-2xl font-bold text-green-500">3</span>
                </div>
                <h3 className="font-bold text-lg mb-2">Reveal</h3>
                <p className="text-sm text-[#a1a1aa]">After 3 turns or success, see your full belief trajectory. Which claims you satisfied, which you violated, and how your understanding evolved.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quote Section */}
      <section className="relative py-24 md:py-32">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-3xl text-center">
            <blockquote className="text-2xl md:text-3xl font-medium leading-relaxed text-foreground">
              &quot;Traditional apps ask: do you know X? LearnLock asks: what do you <span className="text-green-500">believe</span> about X, and <span className="text-green-500">where is it wrong?</span>&quot;
            </blockquote>
            <p className="mt-6 text-[#a1a1aa]">— The Duel Engine Philosophy</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-24 md:py-32 bg-[#1f1f23]/30">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="font-bold text-3xl leading-[1.1] md:text-4xl tracking-tight mb-4">
              Stop consuming. Start retaining.
            </h2>
            <p className="text-lg text-[#a1a1aa] mb-8">
              One pip install. Free API keys. Your data never leaves your machine.
            </p>
            <Link 
              href="/docs"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 text-sm font-medium text-[#a1a1aa] hover:text-foreground transition-colors"
            >
              Read the docs
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-[#1f1f23]/50 border-t border-[#27272a]">
        <div className="container mx-auto px-4">
          <div className="grid gap-8 md:grid-cols-4">
            <div className="space-y-4">
              <div className="flex items-center gap-2 font-bold">
                <Terminal className="h-5 w-5" />
                <span>LearnLock</span>
              </div>
              <p className="text-sm text-[#a1a1aa]">
                Adversarial Socratic learning for developers and researchers.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Documentation</h4>
              <ul className="space-y-2 text-sm text-[#a1a1aa]">
                <li><Link href="/docs" className="hover:text-foreground transition-colors">Introduction</Link></li>
                <li><Link href="/docs/installation" className="hover:text-foreground transition-colors">Installation</Link></li>
                <li><Link href="/docs/quickstart" className="hover:text-foreground transition-colors">Quickstart</Link></li>
                <li><Link href="/docs/commands" className="hover:text-foreground transition-colors">CLI Commands</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Core Concepts</h4>
              <ul className="space-y-2 text-sm text-[#a1a1aa]">
                <li><Link href="/docs/duel-engine" className="hover:text-foreground transition-colors">Duel Engine</Link></li>
                <li><Link href="/docs/socratic-dialogue" className="hover:text-foreground transition-colors">Socratic Dialogue</Link></li>
                <li><Link href="/docs/spaced-repetition" className="hover:text-foreground transition-colors">Spaced Repetition</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Links</h4>
              <ul className="space-y-2 text-sm text-[#a1a1aa]">
                <li><a href="https://github.com/MitudruDutta/learnlock" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">GitHub</a></li>
                <li><a href="https://pypi.org/project/learnlock/" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">PyPI</a></li>
                <li><a href="https://github.com/MitudruDutta/learnlock/issues" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">Issues</a></li>
              </ul>
            </div>
          </div>
          
          <div className="mt-12 pt-8 border-t border-[#27272a] flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-[#a1a1aa]">
            <p>2026 LearnLock. Open source under MIT License.</p>
            <p>LearnLock doesn&apos;t teach you. It finds out what you don&apos;t know.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
