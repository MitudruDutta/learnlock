import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function SpacedRepetitionPage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight mb-3 sm:mb-4">Spaced Repetition</h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground">The SM-2 algorithm that schedules your reviews.</p>
      </div>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Why Spaced Repetition?</h2>
        <p className="text-sm sm:text-base text-muted-foreground">
          Your brain forgets on a predictable curve. Spaced repetition schedules reviews just before 
          you forget — maximizing retention with minimum effort.
        </p>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">The SM-2 Algorithm</h2>
        <p className="text-sm sm:text-base text-muted-foreground">Each concept has three key values:</p>
        <ul className="list-disc list-inside space-y-2 text-sm sm:text-base text-muted-foreground">
          <li><strong className="text-foreground">Ease Factor</strong> — How easy this concept is (starts at 2.5)</li>
          <li><strong className="text-foreground">Interval</strong> — Days until next review</li>
          <li><strong className="text-foreground">Review Count</strong> — How many times reviewed</li>
        </ul>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Interval Progression</h2>
        <p className="text-sm sm:text-base text-muted-foreground">With consistent good scores (4/5):</p>
        <div className="-mx-2 px-2 sm:mx-0 sm:px-0 overflow-x-auto">
          <table className="w-full text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-4 text-muted-foreground">Review #</th>
                <th className="text-left py-2 text-muted-foreground">Interval</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4">1</td>
                <td className="py-2">1 day</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4">2</td>
                <td className="py-2">6 days</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4">3</td>
                <td className="py-2">~2 weeks</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4">4</td>
                <td className="py-2">~5 weeks</td>
              </tr>
              <tr>
                <td className="py-2 pr-4">5+</td>
                <td className="py-2">~3 months (max 180 days)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Pass vs Fail</h2>
        <div className="grid gap-3 sm:gap-4 md:grid-cols-2">
          <div className="p-3 sm:p-4 rounded-lg border border-green-500/30 bg-green-500/5">
            <h3 className="text-base sm:text-lg font-medium text-green-400 mb-2">On Pass (score ≥ 3)</h3>
            <ul className="text-xs sm:text-sm space-y-1 text-muted-foreground">
              <li>Interval increases</li>
              <li>Ease factor adjusts</li>
              <li>Review count +1</li>
            </ul>
          </div>
          <div className="p-3 sm:p-4 rounded-lg border border-red-500/30 bg-red-500/5">
            <h3 className="text-base sm:text-lg font-medium text-red-400 mb-2">On Fail (score &lt; 3)</h3>
            <ul className="text-xs sm:text-sm space-y-1 text-muted-foreground">
              <li>Interval resets to 1 day</li>
              <li>Ease factor decreases</li>
              <li>Review count resets</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Mastery Criteria</h2>
        <p className="text-sm sm:text-base text-muted-foreground">A concept is &quot;mastered&quot; when:</p>
        <ul className="list-disc list-inside space-y-2 text-sm sm:text-base text-muted-foreground">
          <li>Ease factor ≥ 2.5</li>
          <li>Review count ≥ 3</li>
        </ul>
      </section>

      <div className="p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
        <p className="text-xs sm:text-sm text-muted-foreground mb-2">Next:</p>
        <Link href="/docs/commands" className="inline-flex items-center gap-2 text-sm sm:text-base text-foreground hover:underline font-medium">
          CLI Commands <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
