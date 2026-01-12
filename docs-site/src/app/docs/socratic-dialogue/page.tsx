import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function SocraticDialoguePage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight mb-3 sm:mb-4">Socratic Dialogue</h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground">How LearnLock challenges your understanding through adversarial interrogation.</p>
      </div>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">The Socratic Method</h2>
        <p className="text-sm sm:text-base text-muted-foreground">
          Instead of lecturing, the teacher asks probing questions that expose contradictions 
          and gaps in the student&apos;s thinking. LearnLock implements this through the Duel Engine.
        </p>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">How It Works</h2>
        <ol className="list-decimal list-inside space-y-2 text-sm sm:text-base text-muted-foreground">
          <li>You explain a concept in your own words</li>
          <li>The engine infers what you <strong className="text-foreground">believe</strong></li>
          <li>It compares your belief against ground truth claims</li>
          <li>It finds contradictions and attacks the weakest point</li>
          <li>After 3 turns (or success), it reveals your belief trajectory</li>
          <li>Your score feeds into SM-2 spaced repetition scheduling</li>
        </ol>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Dialogue Flow</h2>
        <div className="p-3 sm:p-4 bg-[#1f1f23] border border-[#3f3f46] rounded-lg space-y-3 font-mono text-xs sm:text-sm">
          <p><span className="text-cyan-400">Challenge:</span> What problem does self-attention solve?</p>
          <p><span className="text-muted-foreground">You:</span> It helps focus on important parts.</p>
          <p><span className="text-yellow-400">Attack:</span> That&apos;s vague. WHY is focusing necessary? What limitation does it overcome?</p>
          <p><span className="text-muted-foreground">You:</span> RNNs have the bottleneck problem where information gets compressed...</p>
          <p><span className="text-yellow-400">Attack:</span> Good. But what about training speed? You mentioned nothing about parallelization.</p>
          <p><span className="text-muted-foreground">You:</span> Attention allows parallel computation across all positions...</p>
          <p><span className="text-green-400">Reveal:</span> ████░ Good (4/5) — Trajectory: vague → partial → solid</p>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Engine Behaviors</h2>
        <ul className="list-disc list-inside space-y-2 text-sm sm:text-base text-muted-foreground">
          <li><strong className="text-foreground">Vague answers</strong> → trigger mechanism probes</li>
          <li><strong className="text-foreground">Wrong answers</strong> → trigger claim-specific attacks</li>
          <li><strong className="text-foreground">&quot;I don&apos;t know&quot;</strong> → triggers guiding questions (not punishment)</li>
          <li><strong className="text-foreground">Correct answers</strong> → pass after verification</li>
          <li><strong className="text-foreground">3 turns exhausted</strong> → reveal with full trajectory</li>
        </ul>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Good vs Bad Explanations</h2>
        <div className="space-y-3 sm:space-y-4">
          <div className="p-3 sm:p-4 rounded-lg border border-red-500/30 bg-red-500/5">
            <p className="text-red-400 font-medium text-xs sm:text-sm mb-2">❌ Bad (triggers attack)</p>
            <p className="text-xs sm:text-sm">&quot;Attention helps the model focus on important things.&quot;</p>
            <p className="text-xs text-muted-foreground mt-1">→ Superficial. No mechanism. Will be probed.</p>
          </div>
          <div className="p-3 sm:p-4 rounded-lg border border-green-500/30 bg-green-500/5">
            <p className="text-green-400 font-medium text-xs sm:text-sm mb-2">✓ Good (passes)</p>
            <p className="text-xs sm:text-sm">&quot;Self-attention computes weighted relationships between all positions simultaneously. Unlike RNNs that compress into a fixed hidden state, attention directly connects any two positions, enabling parallel training and avoiding the information bottleneck.&quot;</p>
          </div>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Tip: Double Enter</h2>
        <p className="text-sm sm:text-base text-muted-foreground">
          Press Enter twice to send your answer. This lets you write multi-line explanations.
        </p>
      </section>

      <div className="p-3 sm:p-4 rounded-lg border border-[#3f3f46] bg-[#1f1f23]">
        <p className="text-xs sm:text-sm text-muted-foreground mb-2">Next:</p>
        <Link href="/docs/spaced-repetition" className="inline-flex items-center gap-2 text-sm sm:text-base text-foreground hover:underline font-medium">
          Spaced Repetition <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
