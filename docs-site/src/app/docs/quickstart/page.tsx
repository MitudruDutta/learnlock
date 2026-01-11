import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function QuickstartPage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight mb-3 sm:mb-4">Quick Start</h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground">From zero to studying in 2 minutes.</p>
      </div>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Step 1: Launch LearnLock</h2>
        <pre className="bg-card p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>learnlock</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Step 2: Add Content</h2>
        <p className="text-sm sm:text-base text-muted-foreground">Paste any URL. LearnLock auto-detects the type:</p>
        <pre className="bg-card p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`learnlock> https://youtube.com/watch?v=...

✓ Neural Networks Explained
✓ Added 10 concepts`}</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Step 3: Start Studying</h2>
        <p className="text-sm sm:text-base text-muted-foreground">Press Enter or type /study:</p>
        <pre className="bg-card p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`learnlock> /study

━━━ 1/10: Backpropagation ━━━
Challenge: How does backpropagation update weights?

> It calculates gradients using the chain rule...

████░ Good (4/5)
Next review: in 6 days`}</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Essential Commands</h2>
        <div className="overflow-x-auto -mx-2 px-2 sm:mx-0 sm:px-0">
          <table className="w-full text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-3 sm:pr-4 text-muted-foreground">Command</th>
                <th className="text-left py-2 text-muted-foreground">Description</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400 whitespace-nowrap">/add &lt;url&gt;</td>
                <td className="py-2">Add content from URL</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400">/study</td>
                <td className="py-2">Start study session</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400">/stats</td>
                <td className="py-2">View progress</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400">/due</td>
                <td className="py-2">See what needs review</td>
              </tr>
              <tr>
                <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400">/help</td>
                <td className="py-2">Show all commands</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <div className="p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
        <p className="text-xs sm:text-sm text-muted-foreground mb-2">Learn more:</p>
        <Link href="/docs/adversarial-learning" className="inline-flex items-center gap-2 text-sm sm:text-base text-foreground hover:underline font-medium">
          How Adversarial Learning Works <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
