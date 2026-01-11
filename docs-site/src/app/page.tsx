"use client";

import { HeroSection } from "@/components/blocks/hero-section";
import { Brain, Zap, Terminal, CheckCircle2, ArrowRight } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-3.5rem)]">
      <HeroSection />

      {/* Features Section */}
      <section className="relative py-24 md:py-32 overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-background via-muted/30 to-background" />
        
        <div className="container mx-auto px-4 relative">
          <div className="mx-auto flex max-w-[58rem] flex-col items-center space-y-4 text-center mb-16">
            <span className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Core Features</span>
            <h2 className="font-bold text-3xl leading-[1.1] sm:text-3xl md:text-5xl tracking-tight">
              Built on <span className="text-muted-foreground">proven science.</span>
            </h2>
            <p className="max-w-[85%] leading-normal text-muted-foreground sm:text-lg sm:leading-7">
              Every feature is grounded in decades of cognitive science research. Active recall, spaced repetition, and elaborative interrogation—combined into one tool.
            </p>
          </div>
          
          <div className="mx-auto grid justify-center gap-6 sm:grid-cols-2 md:max-w-[64rem] lg:grid-cols-3">
            <div className="h-full min-h-[320px] w-full bg-card p-8 rounded-xl border border-border/50 hover:border-foreground/20 transition-colors">
              <Brain className="h-10 w-10 text-neutral-400 mb-4" />
              <p className="text-xl font-bold mt-2 text-foreground">
                Adversarial Dialogue
              </p>
              <div className="text-muted-foreground mt-4 text-sm leading-relaxed">
                An AI coach that never accepts vague answers:
                <ul className="list-none mt-4 space-y-2">
                  <FeatureItem title="Probes for precise explanations" />
                  <FeatureItem title="Exposes gaps in understanding" />
                  <FeatureItem title="Forces deeper thinking" />
                </ul>
              </div>
            </div>

            <div className="h-full min-h-[320px] w-full bg-card p-8 rounded-xl border border-border/50 hover:border-foreground/20 transition-colors">
              <Zap className="h-10 w-10 text-yellow-500 mb-4" />
              <p className="text-xl font-bold mt-2 text-foreground">
                SM-2 Scheduling
              </p>
              <div className="text-muted-foreground mt-4 text-sm leading-relaxed">
                The algorithm behind Anki and SuperMemo:
                <ul className="list-none mt-4 space-y-2">
                  <FeatureItem title="Reviews timed to interrupt forgetting" />
                  <FeatureItem title="Intervals adapt to performance" />
                  <FeatureItem title="Long-term retention guaranteed" />
                </ul>
              </div>
            </div>

            <div className="h-full min-h-[320px] w-full bg-card p-8 rounded-xl border border-border/50 hover:border-foreground/20 transition-colors">
              <Terminal className="h-10 w-10 text-blue-500 mb-4" />
              <p className="text-xl font-bold mt-2 text-foreground">
                Terminal Native
              </p>
              <div className="text-muted-foreground mt-4 text-sm leading-relaxed">
                Designed for developers who live in the CLI:
                <ul className="list-none mt-4 space-y-2">
                  <FeatureItem title="All data stored locally" />
                  <FeatureItem title="Zero distractions" />
                  <FeatureItem title="Fully keyboard-driven" />
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="relative py-24 md:py-32 bg-muted/20">
        <div className="container mx-auto px-4">
          <div className="mx-auto flex max-w-[58rem] flex-col items-center space-y-4 text-center mb-16">
            <span className="text-sm font-medium text-muted-foreground uppercase tracking-wider">The Process</span>
            <h2 className="font-bold text-3xl leading-[1.1] sm:text-3xl md:text-5xl tracking-tight">
              From content to <span className="text-muted-foreground">comprehension</span>
            </h2>
          </div>
          
          <div className="mx-auto max-w-4xl">
            <div className="grid gap-8 md:grid-cols-3">
              <div className="relative flex flex-col items-center text-center p-6">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-card mb-4 border border-border/50">
                  <span className="text-2xl font-bold">1</span>
                </div>
                <h3 className="font-bold text-lg mb-2">Ingest</h3>
                <p className="text-sm text-muted-foreground">Point LearnLock at any resource—videos, articles, papers, repos. It extracts atomic concepts automatically.</p>
              </div>
              
              <div className="relative flex flex-col items-center text-center p-6">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-card mb-4 border border-border/50">
                  <span className="text-2xl font-bold">2</span>
                </div>
                <h3 className="font-bold text-lg mb-2">Defend</h3>
                <p className="text-sm text-muted-foreground">Explain each concept. The coach will probe, question, and push back until your understanding is airtight.</p>
              </div>
              
              <div className="relative flex flex-col items-center text-center p-6">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-card mb-4 border border-border/50">
                  <span className="text-2xl font-bold">3</span>
                </div>
                <h3 className="font-bold text-lg mb-2">Retain</h3>
                <p className="text-sm text-muted-foreground">Reviews are scheduled at scientifically optimal intervals. What you learn stays with you permanently.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonial / Quote Section */}
      <section className="relative py-24 md:py-32">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-3xl text-center">
            <blockquote className="text-2xl md:text-3xl font-medium leading-relaxed text-foreground">
              &quot;The best learning happens when you&apos;re forced to <span className="text-muted-foreground">explain</span>, <span className="text-muted-foreground">defend</span>, and <span className="text-muted-foreground">question</span> what you think you know.&quot;
            </blockquote>
            <p className="mt-6 text-muted-foreground">— The Philosophy Behind LearnLock</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-24 md:py-32 bg-gradient-to-b from-muted/30 to-background">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="font-bold text-3xl leading-[1.1] md:text-4xl tracking-tight mb-4">
              Start learning with intention.
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              One command to install. Free forever. Your data stays on your machine.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="rounded-full h-12 px-8">
                <Link href="/docs/installation">
                    Get Started Free
                </Link>
              </Button>
              <Link 
                href="/docs"
                className="inline-flex items-center justify-center gap-2 px-6 py-3 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Read the docs
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-card/50 border-t border-border/50">
        <div className="container mx-auto px-4">
          <div className="grid gap-8 md:grid-cols-4">
            <div className="space-y-4">
              <div className="flex items-center gap-2 font-bold">
                <Terminal className="h-5 w-5" />
                <span>LearnLock</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Adversarial learning for developers and researchers.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Documentation</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/docs" className="hover:text-foreground transition-colors">Introduction</Link></li>
                <li><Link href="/docs/installation" className="hover:text-foreground transition-colors">Installation</Link></li>
                <li><Link href="/docs/quickstart" className="hover:text-foreground transition-colors">Quickstart</Link></li>
                <li><Link href="/docs/commands" className="hover:text-foreground transition-colors">CLI Commands</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Concepts</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/docs/adversarial-learning" className="hover:text-foreground transition-colors">Adversarial Learning</Link></li>
                <li><Link href="/docs/socratic-dialogue" className="hover:text-foreground transition-colors">Socratic Dialogue</Link></li>
                <li><Link href="/docs/spaced-repetition" className="hover:text-foreground transition-colors">Spaced Repetition</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Links</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="https://github.com/MitudruDutta/learnlock" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">GitHub</a></li>
                <li><a href="https://github.com/MitudruDutta/learnlock/issues" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">Issues</a></li>
                <li><a href="https://github.com/MitudruDutta/learnlock/releases" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">Releases</a></li>
              </ul>
            </div>
          </div>
          
          <div className="mt-12 pt-8 border-t border-border/50 flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
            <p>2026 LearnLock. Open source under MIT License.</p>
            <p>For learners who demand more than surface-level understanding.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

const FeatureItem = ({ title }: { title: string }) => {
  return (
    <li className="flex gap-2 items-start">
      <CheckCircle2 className="h-4 w-4 text-neutral-500 mt-0.5 shrink-0" />
      <p className="text-muted-foreground text-sm">{title}</p>
    </li>
  );
};
