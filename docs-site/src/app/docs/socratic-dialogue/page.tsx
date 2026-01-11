import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function SocraticDialoguePage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight mb-3 sm:mb-4">Socratic Dialogue</h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground">How LearnLock challenges your understanding.</p>
      </div>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">The Socratic Method</h2>
        <p className="text-sm sm:text-base text-muted-foreground">
          Instead of lecturing, the teacher asks probing questions that expose contradictions 
          and gaps in the student&apos;s thinking. LearnLock implements this through adversarial dialogue.
        </p>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Dialogue Flow</h2>
        <div className="p-3 sm:p-4 bg-card rounded-lg space-y-3 font-mono text-xs sm:text-sm">
          <p><span className="text-cyan-400">Challenge:</span> What problem does self-attention solve?</p>
          <p><span className="text-muted-foreground">User:</span> It helps focus on important parts.</p>
          <p><span className="text-yellow-400">Follow-up:</span> That&apos;s vague. WHY is focusing necessary?</p>
          <p><span className="text-muted-foreground">User:</span> RNNs have the bottleneck problem...</p>
          <p><span className="text-yellow-400">Follow-up:</span> Good. But what about training speed?</p>
          <p><span className="text-muted-foreground">User:</span> Attention allows parallel computation...</p>
          <p><span className="text-green-400">Final:</span> ████░ Good (4/5)</p>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">How Holes Are Detected</h2>
        <ul className="list-disc list-inside space-y-2 text-sm sm:text-base text-muted-foreground">
          <li><strong className="text-foreground">Vagueness</strong> — Generic statements without specifics</li>
          <li><strong className="text-foreground">Misconceptions</strong> — Factually incorrect claims</li>
          <li><strong className="text-foreground">Oversimplifications</strong> — Missing important nuances</li>
          <li><strong className="text-foreground">Missing key points</strong> — Core concepts not mentioned</li>
        </ul>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Turn Limits</h2>
        <p className="text-sm sm:text-base text-muted-foreground">
          The dialogue continues for up to <strong className="text-foreground">3 turns</strong> or until no more holes are found.
          Each hole found reduces your score by 1 point.
        </p>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Good vs Bad Explanations</h2>
        <div className="space-y-3 sm:space-y-4">
          <div className="p-3 sm:p-4 rounded-lg border border-red-500/30 bg-red-500/5">
            <p className="text-red-400 font-medium text-xs sm:text-sm mb-2">❌ Bad</p>
            <p className="text-xs sm:text-sm">&quot;Attention helps the model focus on important things.&quot;</p>
          </div>
          <div className="p-3 sm:p-4 rounded-lg border border-green-500/30 bg-green-500/5">
            <p className="text-green-400 font-medium text-xs sm:text-sm mb-2">✓ Good</p>
            <p className="text-xs sm:text-sm">&quot;Self-attention computes weighted relationships between all positions simultaneously. Unlike RNNs that compress into a fixed hidden state, attention directly connects any two positions.&quot;</p>
          </div>
        </div>
      </section>

      <div className="p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
        <p className="text-xs sm:text-sm text-muted-foreground mb-2">Next:</p>
        <Link href="/docs/spaced-repetition" className="inline-flex items-center gap-2 text-sm sm:text-base text-foreground hover:underline font-medium">
          Spaced Repetition (SM-2) <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
