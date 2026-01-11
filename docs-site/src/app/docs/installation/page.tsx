"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function InstallationPage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight mb-3 sm:mb-4">Installation</h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground">Get LearnLock running in under 5 minutes.</p>
      </div>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">pip (Recommended)</h2>
        <pre className="bg-muted p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>pip install learnlock</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">curl (macOS/Linux)</h2>
        <pre className="bg-muted p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code className="break-all sm:break-normal">curl -fsSL https://raw.githubusercontent.com/MitudruDutta/learnlock/main/install.sh | bash</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">From Source</h2>
        <pre className="bg-muted p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`git clone https://github.com/MitudruDutta/learnlock.git
cd learnlock
pip install -e .`}</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">API Keys Setup</h2>
        <p className="text-sm sm:text-base text-muted-foreground">LearnLock requires at least one API key. Both are free.</p>
        
        <h3 className="text-base sm:text-lg font-medium mt-3 sm:mt-4">1. Groq API Key (Required)</h3>
        <ol className="list-decimal list-inside space-y-1.5 sm:space-y-2 text-sm sm:text-base text-muted-foreground">
          <li>Go to <a href="https://console.groq.com" className="text-foreground underline">console.groq.com</a></li>
          <li>Create an account (free)</li>
          <li>Generate an API key</li>
        </ol>

        <h3 className="text-base sm:text-lg font-medium mt-3 sm:mt-4">2. Gemini API Key (Recommended)</h3>
        <ol className="list-decimal list-inside space-y-1.5 sm:space-y-2 text-sm sm:text-base text-muted-foreground">
          <li>Go to <a href="https://aistudio.google.com" className="text-foreground underline">aistudio.google.com</a></li>
          <li>Sign in with Google</li>
          <li>Get API key</li>
        </ol>

        <h3 className="text-base sm:text-lg font-medium mt-3 sm:mt-4">Set Environment Variables</h3>
        <p className="text-xs sm:text-sm text-muted-foreground mb-2">macOS/Linux:</p>
        <pre className="bg-muted p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`export GROQ_API_KEY=your_groq_key
export GEMINI_API_KEY=your_gemini_key`}</code></pre>

        <p className="text-xs sm:text-sm text-muted-foreground mb-2 mt-3 sm:mt-4">Windows (PowerShell):</p>
        <pre className="bg-muted p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`$env:GROQ_API_KEY="your_groq_key"
$env:GEMINI_API_KEY="your_gemini_key"`}</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Verify Installation</h2>
        <pre className="bg-muted p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>learnlock --version</code></pre>
      </section>

      <div className="p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
        <p className="text-xs sm:text-sm text-muted-foreground mb-2">Next step:</p>
        <Link href="/docs/quickstart" className="inline-flex items-center gap-2 text-sm sm:text-base text-foreground hover:underline font-medium">
          Quick Start Guide <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}