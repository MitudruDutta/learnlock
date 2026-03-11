import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function StudySessionsPage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight mb-3 sm:mb-4">Study Sessions</h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground">How to get the most out of adversarial study.</p>
      </div>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Starting a Session</h2>
        <pre className="bg-[#1f1f23] border border-[#3f3f46] p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`learnlock> /study
# or just press Enter
	
DUEL SESSION - 5 concepts
Type 'skip' to skip, 'q' to quit.
Double Enter submits your answer.`}</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Session Flow</h2>
        <ol className="list-decimal list-inside space-y-2 text-sm sm:text-base text-muted-foreground">
          <li>See the concept name, source, and current challenge</li>
          <li>Type your explanation and press Enter twice to submit</li>
          <li>LearnLock models your belief and probes the weakest claim</li>
          <li>Low-confidence findings are shown, but they are down-weighted before scoring</li>
          <li>After up to 3 rounds, you get a reveal and the next review date</li>
        </ol>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Writing Good Explanations</h2>
        <div className="space-y-3 sm:space-y-4">
          <div className="p-3 sm:p-4 rounded-lg border border-red-500/30 bg-red-500/5">
            <p className="text-red-400 font-medium text-xs sm:text-sm mb-2">BAD - Too Vague</p>
            <p className="text-xs sm:text-sm">&quot;Backpropagation updates weights using gradients.&quot;</p>
          </div>
          <div className="p-3 sm:p-4 rounded-lg border border-green-500/30 bg-green-500/5">
            <p className="text-green-400 font-medium text-xs sm:text-sm mb-2">GOOD - Specific</p>
            <p className="text-xs sm:text-sm">&quot;Backpropagation computes gradients via chain rule on the computational graph. Starting from loss, it calculates dL/dw for each weight by multiplying local gradients backward.&quot;</p>
          </div>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Using Images (OCR)</h2>
        <p className="text-sm sm:text-base text-muted-foreground">Answer with a photo of handwritten notes:</p>
        <pre className="bg-[#1f1f23] border border-[#3f3f46] p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`> /path/to/notes.jpg

Extracting text from image...
Extracted: "Backpropagation uses chain rule..."`}</code></pre>
        <p className="text-xs sm:text-sm text-muted-foreground mt-2">
          Requires: <code className="bg-[#1f1f23] px-1 rounded">pip install learnlock[ocr]</code>
        </p>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">YouTube Review Links and /visual</h2>
        <p className="text-sm sm:text-base text-muted-foreground">
          For YouTube concepts, LearnLock now shows a transcript-linked timestamp after the reveal.
          If you want to inspect the actual frame, opt in manually.
        </p>
        <pre className="bg-[#1f1f23] border border-[#3f3f46] p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`Review at 12:42: https://youtube.com/watch?v=...&t=762
Type /visual to inspect the on-screen frame for this moment.

learnlock> /visual`}</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Understanding Scores</h2>
        <div className="p-3 sm:p-4 bg-[#1f1f23] border border-[#3f3f46] rounded-lg font-mono text-xs sm:text-sm space-y-1">
          <p><span className="text-cyan-400">|||||</span> Perfect (5) - No holes found</p>
          <p><span className="text-green-400">||||.</span> Great (4) - Minor gaps</p>
          <p><span className="text-yellow-400">|||..</span> Good (3) - Some gaps</p>
          <p><span className="text-red-400">|....</span> Needs Work (1) - Critical errors remain</p>
        </div>
        <p className="text-xs sm:text-sm text-muted-foreground">
          Scores are intentionally coarse. LearnLock currently uses 5, 4, 3, and 1;
          low-confidence findings can be surfaced in the reveal without dragging you all the
          way down to a failing score.
        </p>
      </section>

      <div className="p-3 sm:p-4 rounded-lg border border-[#3f3f46] bg-[#1f1f23]">
        <p className="text-xs sm:text-sm text-muted-foreground mb-2">Next:</p>
        <Link href="/docs/configuration" className="inline-flex items-center gap-2 text-sm sm:text-base text-foreground hover:underline font-medium">
          Configuration <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
