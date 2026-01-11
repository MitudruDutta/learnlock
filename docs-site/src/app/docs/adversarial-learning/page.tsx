import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function AdversarialLearningPage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight mb-3 sm:mb-4">Adversarial Learning</h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground">The philosophy behind LearnLock.</p>
      </div>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">The Problem with Passive Learning</h2>
        <p className="text-sm sm:text-base text-muted-foreground">
          You watch a video. You read an article. You feel like you understand. But when someone asks 
          you to explain it, you stumble. This is the <strong className="text-foreground">illusion of competence</strong>.
        </p>
        <p className="text-sm sm:text-base text-muted-foreground">
          Your brain confuses recognition with recall. LearnLock forces active recall by making you 
          explain concepts, then systematically exposes what you think you know vs what you actually know.
        </p>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">The Pipeline</h2>
        <div className="space-y-3 sm:space-y-4">
          <div className="flex items-start gap-3 sm:gap-4 p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
            <span className="flex h-6 w-6 sm:h-8 sm:w-8 items-center justify-center rounded-full bg-foreground text-background text-sm sm:text-base font-bold shrink-0">1</span>
            <div>
              <h3 className="font-medium text-sm sm:text-base">Add</h3>
              <p className="text-xs sm:text-sm text-muted-foreground">YouTube, article, PDF, or GitHub URL</p>
            </div>
          </div>
          <div className="flex items-start gap-3 sm:gap-4 p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
            <span className="flex h-6 w-6 sm:h-8 sm:w-8 items-center justify-center rounded-full bg-foreground text-background text-sm sm:text-base font-bold shrink-0">2</span>
            <div>
              <h3 className="font-medium text-sm sm:text-base">Extract</h3>
              <p className="text-xs sm:text-sm text-muted-foreground">LLM identifies 8-12 key concepts with challenge questions</p>
            </div>
          </div>
          <div className="flex items-start gap-3 sm:gap-4 p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
            <span className="flex h-6 w-6 sm:h-8 sm:w-8 items-center justify-center rounded-full bg-foreground text-background text-sm sm:text-base font-bold shrink-0">3</span>
            <div>
              <h3 className="font-medium text-sm sm:text-base">Challenge</h3>
              <p className="text-xs sm:text-sm text-muted-foreground">You explain, it finds holes in your understanding</p>
            </div>
          </div>
          <div className="flex items-start gap-3 sm:gap-4 p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
            <span className="flex h-6 w-6 sm:h-8 sm:w-8 items-center justify-center rounded-full bg-foreground text-background text-sm sm:text-base font-bold shrink-0">4</span>
            <div>
              <h3 className="font-medium text-sm sm:text-base">Probe</h3>
              <p className="text-xs sm:text-sm text-muted-foreground">Up to 3 rounds of Socratic follow-ups</p>
            </div>
          </div>
          <div className="flex items-start gap-3 sm:gap-4 p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
            <span className="flex h-6 w-6 sm:h-8 sm:w-8 items-center justify-center rounded-full bg-foreground text-background text-sm sm:text-base font-bold shrink-0">5</span>
            <div>
              <h3 className="font-medium text-sm sm:text-base">Score</h3>
              <p className="text-xs sm:text-sm text-muted-foreground">1-5 based on gaps exposed, not what you got right</p>
            </div>
          </div>
          <div className="flex items-start gap-3 sm:gap-4 p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
            <span className="flex h-6 w-6 sm:h-8 sm:w-8 items-center justify-center rounded-full bg-foreground text-background text-sm sm:text-base font-bold shrink-0">6</span>
            <div>
              <h3 className="font-medium text-sm sm:text-base">Schedule</h3>
              <p className="text-xs sm:text-sm text-muted-foreground">SM-2 brings weak concepts back at optimal intervals</p>
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Scoring Philosophy</h2>
        <p className="text-sm sm:text-base text-muted-foreground">
          Unlike traditional flashcards that reward correct answers, LearnLock scores based on <strong className="text-foreground">gaps exposed</strong>:
        </p>
        <div className="overflow-x-auto -mx-2 px-2 sm:mx-0 sm:px-0">
          <table className="w-full text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-3 sm:pr-4 text-muted-foreground whitespace-nowrap">Score</th>
                <th className="text-left py-2 text-muted-foreground">Meaning</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 text-red-400 whitespace-nowrap">1 - Needs Work</td>
                <td className="py-2">Major gaps, fundamental misunderstanding</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 text-orange-400 whitespace-nowrap">2 - Getting There</td>
                <td className="py-2">Multiple holes exposed</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 text-yellow-400 whitespace-nowrap">3 - Good</td>
                <td className="py-2">Solid base, some gaps</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-3 sm:pr-4 text-green-400 whitespace-nowrap">4 - Great</td>
                <td className="py-2">Minor gaps only</td>
              </tr>
              <tr>
                <td className="py-2 pr-3 sm:pr-4 text-cyan-400 whitespace-nowrap">5 - Perfect</td>
                <td className="py-2">No holes found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <div className="p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
        <p className="text-xs sm:text-sm text-muted-foreground mb-2">Deep dive:</p>
        <Link href="/docs/socratic-dialogue" className="inline-flex items-center gap-2 text-sm sm:text-base text-foreground hover:underline font-medium">
          Socratic Dialogue System <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
