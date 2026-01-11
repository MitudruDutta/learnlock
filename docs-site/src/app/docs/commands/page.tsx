import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function CommandsPage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight mb-3 sm:mb-4">CLI Commands</h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground">Complete reference for all LearnLock commands.</p>
      </div>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Command Overview</h2>
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
                <td className="py-2">Add content from URL or file</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400">/study</td>
                <td className="py-2">Start study session</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400">/stats</td>
                <td className="py-2">Show progress statistics</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400">/list</td>
                <td className="py-2">List all concepts</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400">/due</td>
                <td className="py-2">Show concepts due for review</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400 whitespace-nowrap">/skip &lt;name&gt;</td>
                <td className="py-2">Skip a concept</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400 whitespace-nowrap">/unskip &lt;name&gt;</td>
                <td className="py-2">Restore skipped concept</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400">/config</td>
                <td className="py-2">Show configuration</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400">/help</td>
                <td className="py-2">Show help</td>
              </tr>
              <tr>
                <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400">/quit</td>
                <td className="py-2">Exit LearnLock</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">/add</h2>
        <p className="text-sm sm:text-base text-muted-foreground">Add content from URL or local file:</p>
        <pre className="bg-card p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`# YouTube
learnlock> /add https://youtube.com/watch?v=...

# Article
learnlock> /add https://example.com/article

# GitHub
learnlock> /add https://github.com/user/repo

# PDF
learnlock> /add /path/to/document.pdf`}</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">/study</h2>
        <p className="text-sm sm:text-base text-muted-foreground">Start an adversarial study session:</p>
        <pre className="bg-card p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`learnlock> /study

Study Session — 5 concepts to review
Type 'skip' to skip, 'q' to quit`}</code></pre>
        <p className="text-xs sm:text-sm text-muted-foreground mt-2">
          During study: type <code className="bg-card px-1 rounded">skip</code> to skip, <code className="bg-card px-1 rounded">q</code> to quit.
        </p>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">/stats</h2>
        <pre className="bg-card p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`learnlock> /stats

╭──────────────────────────╮
│      Your Progress       │
├──────────────────────────┤
│ Sources         3        │
│ Concepts        28       │
│ Due now         5        │
│ Avg score       3.8/5    │
│ Mastered        12       │
╰──────────────────────────╯`}</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Aliases</h2>
        <ul className="list-disc list-inside space-y-1 text-xs sm:text-sm text-muted-foreground">
          <li><code className="bg-card px-1 rounded">/list</code> → <code className="bg-card px-1 rounded">/ls</code></li>
          <li><code className="bg-card px-1 rounded">/help</code> → <code className="bg-card px-1 rounded">/h</code>, <code className="bg-card px-1 rounded">/?</code></li>
          <li><code className="bg-card px-1 rounded">/clear</code> → <code className="bg-card px-1 rounded">/cls</code></li>
          <li><code className="bg-card px-1 rounded">/quit</code> → <code className="bg-card px-1 rounded">/exit</code>, <code className="bg-card px-1 rounded">/q</code></li>
        </ul>
      </section>

      <div className="p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
        <p className="text-xs sm:text-sm text-muted-foreground mb-2">Next:</p>
        <Link href="/docs/adding-content" className="inline-flex items-center gap-2 text-sm sm:text-base text-foreground hover:underline font-medium">
          Adding Content <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
