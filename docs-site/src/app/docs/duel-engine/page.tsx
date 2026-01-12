import Link from "next/link";
import { ArrowRight, ArrowDown } from "lucide-react";

function ArchitectureDiagram() {
  return (
    <div className="p-4 sm:p-6 bg-[#1f1f23] rounded-lg border border-[#3f3f46] overflow-x-auto">
      <div className="min-w-[500px] flex flex-col items-center gap-2">
        {/* Top row */}
        <div className="flex gap-3 justify-center flex-wrap">
          <div className="px-3 py-2 bg-blue-500/10 border border-blue-500/30 rounded text-xs sm:text-sm text-blue-400 text-center">
            YouTube
          </div>
          <div className="px-3 py-2 bg-blue-500/10 border border-blue-500/30 rounded text-xs sm:text-sm text-blue-400 text-center">
            Article
          </div>
          <div className="px-3 py-2 bg-blue-500/10 border border-blue-500/30 rounded text-xs sm:text-sm text-blue-400 text-center">
            PDF
          </div>
          <div className="px-3 py-2 bg-blue-500/10 border border-blue-500/30 rounded text-xs sm:text-sm text-blue-400 text-center">
            GitHub
          </div>
        </div>
        
        <ArrowDown className="h-4 w-4 text-muted-foreground" />
        
        {/* LLM Extract */}
        <div className="px-4 py-2 bg-purple-500/10 border border-purple-500/30 rounded text-xs sm:text-sm text-purple-400">
          LLM Extract → 8-12 Concepts + Claims
        </div>
        
        <ArrowDown className="h-4 w-4 text-muted-foreground" />
        
        {/* Three-pass filter */}
        <div className="flex gap-2 items-center">
          <div className="px-2 py-1 bg-yellow-500/10 border border-yellow-500/30 rounded text-xs text-yellow-400">
            Generate
          </div>
          <span className="text-muted-foreground">→</span>
          <div className="px-2 py-1 bg-yellow-500/10 border border-yellow-500/30 rounded text-xs text-yellow-400">
            Garbage Filter
          </div>
          <span className="text-muted-foreground">→</span>
          <div className="px-2 py-1 bg-yellow-500/10 border border-yellow-500/30 rounded text-xs text-yellow-400">
            Sharpness Filter
          </div>
        </div>
        
        <ArrowDown className="h-4 w-4 text-muted-foreground" />
        
        {/* Duel Engine */}
        <div className="px-6 py-3 bg-red-500/10 border border-red-500/30 rounded text-sm sm:text-base text-red-400 font-medium">
          Duel Engine
        </div>
        
        <div className="flex gap-4 text-xs text-muted-foreground">
          <span>Belief Model</span>
          <span>•</span>
          <span>Contradiction Detect</span>
          <span>•</span>
          <span>Interrogate</span>
        </div>
        
        <ArrowDown className="h-4 w-4 text-muted-foreground" />
        
        {/* Bottom row */}
        <div className="flex gap-4">
          <div className="px-3 py-2 bg-green-500/10 border border-green-500/30 rounded text-xs sm:text-sm text-green-400">
            HUD (Rich)
          </div>
          <div className="px-3 py-2 bg-cyan-500/10 border border-cyan-500/30 rounded text-xs sm:text-sm text-cyan-400">
            SM-2 Scheduler
          </div>
          <div className="px-3 py-2 bg-orange-500/10 border border-orange-500/30 rounded text-xs sm:text-sm text-orange-400">
            SQLite
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DuelEnginePage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight mb-3 sm:mb-4">The Duel Engine</h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground">The cognitive core of LearnLock. Located in <code className="bg-[#1f1f23] px-1 rounded">duel.py</code>.</p>
      </div>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Philosophy</h2>
        <p className="text-sm sm:text-base text-muted-foreground">Traditional learning apps ask: &quot;Do you know X?&quot;</p>
        <p className="text-sm sm:text-base text-foreground font-medium">LearnLock asks: &quot;What do you <em>believe</em> about X, and where is it wrong?&quot;</p>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Architecture</h2>
        <ArchitectureDiagram />
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Pipeline</h2>
        <ol className="list-decimal list-inside space-y-2 text-sm sm:text-base text-muted-foreground">
          <li><strong className="text-foreground">Belief Modeling</strong> — Infers what the user thinks from their response</li>
          <li><strong className="text-foreground">Contradiction Detection</strong> — Compares belief against claims, finds violations</li>
          <li><strong className="text-foreground">Interrogation</strong> — Generates attack question targeting highest-severity error</li>
          <li><strong className="text-foreground">Snapshot</strong> — Records belief state for trajectory tracking</li>
        </ol>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Behaviors</h2>
        <ul className="list-disc list-inside space-y-2 text-sm sm:text-base text-muted-foreground">
          <li>Vague answers trigger mechanism probes</li>
          <li>Wrong answers trigger claim-specific attacks</li>
          <li>&quot;I don&apos;t know&quot; triggers guiding questions (not punishment)</li>
          <li>Correct answers pass after verification</li>
          <li>3 turns exhausted triggers reveal with full trajectory</li>
        </ul>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Graded Harshness</h2>
        <p className="text-sm sm:text-base text-muted-foreground mb-3">The engine gets progressively stricter:</p>
        <div className="-mx-2 px-2 sm:mx-0 sm:px-0 overflow-x-auto">
          <table className="w-full text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-4 text-muted-foreground">Turn</th>
                <th className="text-left py-2 text-muted-foreground">Behavior</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4 font-mono text-green-400">Turn 1</td>
                <td className="py-2">Forgiving — only clear violations flagged</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4 font-mono text-yellow-400">Turn 2</td>
                <td className="py-2">Moderate — violations plus omissions</td>
              </tr>
              <tr>
                <td className="py-2 pr-4 font-mono text-red-400">Turn 3</td>
                <td className="py-2">Strict — all violations surfaced</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Error Types</h2>
        <div className="-mx-2 px-2 sm:mx-0 sm:px-0 overflow-x-auto">
          <table className="w-full text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-4 text-muted-foreground">Type</th>
                <th className="text-left py-2 text-muted-foreground">Description</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4 font-mono text-cyan-400">wrong_mechanism</td>
                <td className="py-2">Incorrect explanation of how something works</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4 font-mono text-cyan-400">missing_mechanism</td>
                <td className="py-2">Omitted critical mechanism</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4 font-mono text-cyan-400">boundary_error</td>
                <td className="py-2">Wrong about limitations or scope</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4 font-mono text-cyan-400">conflation</td>
                <td className="py-2">Confused two distinct concepts</td>
              </tr>
              <tr>
                <td className="py-2 pr-4 font-mono text-cyan-400">superficial</td>
                <td className="py-2">Surface-level understanding without depth</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Claim Pipeline</h2>
        <p className="text-sm sm:text-base text-muted-foreground mb-3">Claims are the epistemic foundation. The duel is only as fair as the claims.</p>
        
        <h3 className="text-base sm:text-lg font-medium mt-4">Three-Pass Verification</h3>
        <div className="space-y-3">
          <div className="p-3 sm:p-4 rounded-lg border border-[#3f3f46] bg-[#1f1f23]">
            <p className="text-cyan-400 font-medium text-xs sm:text-sm mb-1">Pass 1: Generation</p>
            <p className="text-xs sm:text-sm text-muted-foreground">LLM generates claims with explicit instructions to produce conceptual truths, not transcript parroting. Demands falsifiable statements about WHY and HOW.</p>
          </div>
          <div className="p-3 sm:p-4 rounded-lg border border-[#3f3f46] bg-[#1f1f23]">
            <p className="text-yellow-400 font-medium text-xs sm:text-sm mb-1">Pass 2: Garbage Filter</p>
            <p className="text-xs sm:text-sm text-muted-foreground">Pattern matching rejects stateful claims (&quot;is running&quot;), tautologies (&quot;processes requests&quot;), and vague claims (&quot;is useful&quot;).</p>
          </div>
          <div className="p-3 sm:p-4 rounded-lg border border-[#3f3f46] bg-[#1f1f23]">
            <p className="text-green-400 font-medium text-xs sm:text-sm mb-1">Pass 3: Sharpness Filter</p>
            <p className="text-xs sm:text-sm text-muted-foreground">Rejects blurry truths that are technically correct but unfalsifiable (&quot;handles security&quot;, &quot;manages data&quot;).</p>
          </div>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Claim Types</h2>
        <ul className="list-disc list-inside space-y-2 text-sm sm:text-base text-muted-foreground">
          <li><strong className="text-foreground">definition</strong> — What the concept is</li>
          <li><strong className="text-foreground">mechanism</strong> — How it works internally</li>
          <li><strong className="text-foreground">requirement</strong> — What it needs to function</li>
          <li><strong className="text-foreground">boundary</strong> — What it cannot do or where it fails</li>
        </ul>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Good vs Bad Claims</h2>
        <div className="space-y-3">
          <div className="p-3 sm:p-4 rounded-lg border border-red-500/30 bg-red-500/5">
            <p className="text-red-400 font-medium text-xs sm:text-sm mb-2">❌ Bad (rejected)</p>
            <ul className="text-xs sm:text-sm space-y-1 text-muted-foreground">
              <li>&quot;The server processes requests&quot; (tautology)</li>
              <li>&quot;It handles security&quot; (blurry)</li>
              <li>&quot;Must be running to work&quot; (stateful)</li>
            </ul>
          </div>
          <div className="p-3 sm:p-4 rounded-lg border border-green-500/30 bg-green-500/5">
            <p className="text-green-400 font-medium text-xs sm:text-sm mb-2">✓ Good (survives)</p>
            <ul className="text-xs sm:text-sm space-y-1 text-muted-foreground">
              <li>&quot;Validates request payloads against a JSON schema&quot;</li>
              <li>&quot;Enforces authentication via JWT token verification&quot;</li>
              <li>&quot;Uses Python type hints for automatic request validation&quot;</li>
            </ul>
          </div>
        </div>
      </section>

      <div className="p-3 sm:p-4 rounded-lg border border-[#3f3f46] bg-[#1f1f23]">
        <p className="text-xs sm:text-sm text-muted-foreground mb-2">Next:</p>
        <Link href="/docs/study-sessions" className="inline-flex items-center gap-2 text-sm sm:text-base text-foreground hover:underline font-medium">
          Study Sessions <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
