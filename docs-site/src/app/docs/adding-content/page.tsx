import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function AddingContentPage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight mb-3 sm:mb-4">Adding Content</h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground">How to add YouTube, articles, PDFs, and GitHub repos.</p>
      </div>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Supported Sources</h2>
        <div className="grid gap-3 sm:gap-4 md:grid-cols-2">
          <div className="p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
            <h3 className="text-base sm:text-lg font-medium">YouTube</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">Transcripts via API, Whisper fallback</p>
          </div>
          <div className="p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
            <h3 className="text-base sm:text-lg font-medium">Articles</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">Web content via Trafilatura</p>
          </div>
          <div className="p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
            <h3 className="text-base sm:text-lg font-medium">PDFs</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">Local files or URLs via PyMuPDF</p>
          </div>
          <div className="p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
            <h3 className="text-base sm:text-lg font-medium">GitHub</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">README extraction via API</p>
          </div>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Examples</h2>
        <pre className="bg-card p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`# YouTube video
learnlock> https://youtube.com/watch?v=...

# Web article
learnlock> https://example.com/blog/post

# GitHub repository
learnlock> https://github.com/user/repo

# Local PDF
learnlock> /path/to/document.pdf

# PDF URL
learnlock> https://arxiv.org/pdf/1234.5678.pdf`}</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">What Gets Extracted</h2>
        <p className="text-sm sm:text-base text-muted-foreground">For each source, LearnLock:</p>
        <ol className="list-decimal list-inside space-y-2 text-sm sm:text-base text-muted-foreground">
          <li>Generates a topic-based title (3-7 words)</li>
          <li>Extracts 3-20 key concepts</li>
          <li>Creates a challenge question for each</li>
          <li>Pulls a source quote for context</li>
        </ol>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Duplicate Detection</h2>
        <pre className="bg-card p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`learnlock> https://youtube.com/watch?v=...

Already added: Neural Networks Explained
10 concepts`}</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Limits</h2>
        <ul className="list-disc list-inside space-y-1 text-sm sm:text-base text-muted-foreground">
          <li>Content truncated to 8,000 characters</li>
          <li>Concept names max 200 characters</li>
          <li>Source quotes max 500 characters</li>
          <li>3-20 concepts per source</li>
        </ul>
      </section>

      <div className="p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
        <p className="text-xs sm:text-sm text-muted-foreground mb-2">Next:</p>
        <Link href="/docs/ocr" className="inline-flex items-center gap-2 text-sm sm:text-base text-foreground hover:underline font-medium">
          OCR Support <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
