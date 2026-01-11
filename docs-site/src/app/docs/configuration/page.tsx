import Link from "next/link";

export default function ConfigurationPage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight mb-3 sm:mb-4">Configuration</h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground">All configurable options via environment variables.</p>
      </div>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">View Current Config</h2>
        <pre className="bg-card p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`learnlock> /config

Configuration:
  Data directory: ~/.learnlock
  Database: ~/.learnlock/data.db
  Groq model: llama-3.3-70b-versatile
  Gemini model: gemini-2.5-flash
  GROQ_API_KEY: set
  GEMINI_API_KEY: set`}</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Required</h2>
        <div className="-mx-2 px-2 sm:mx-0 sm:px-0 overflow-x-auto">
          <table className="w-full text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-4 text-muted-foreground">Variable</th>
                <th className="text-left py-2 text-muted-foreground">Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="py-2 pr-4 font-mono text-cyan-400">GROQ_API_KEY</td>
                <td className="py-2">Groq API key (free at console.groq.com)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Recommended</h2>
        <div className="-mx-2 px-2 sm:mx-0 sm:px-0 overflow-x-auto">
          <table className="w-full text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-4 text-muted-foreground">Variable</th>
                <th className="text-left py-2 text-muted-foreground">Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="py-2 pr-4 font-mono text-cyan-400">GEMINI_API_KEY</td>
                <td className="py-2">Gemini API key (free at aistudio.google.com)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Paths</h2>
        <div className="-mx-2 px-2 sm:mx-0 sm:px-0 overflow-x-auto">
          <table className="w-full text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-4 text-muted-foreground">Variable</th>
                <th className="text-left py-2 pr-4 text-muted-foreground">Default</th>
                <th className="text-left py-2 text-muted-foreground">Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="py-2 pr-4 font-mono text-cyan-400">LEARNLOCK_DATA_DIR</td>
                <td className="py-2 pr-4 font-mono text-muted-foreground">~/.learnlock</td>
                <td className="py-2">Data directory</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">LLM Models</h2>
        <div className="-mx-2 px-2 sm:mx-0 sm:px-0 overflow-x-auto">
          <table className="w-full text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-4 text-muted-foreground">Variable</th>
                <th className="text-left py-2 pr-4 text-muted-foreground">Default</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4 font-mono text-cyan-400">LEARNLOCK_GROQ_MODEL</td>
                <td className="py-2 pr-4 font-mono text-muted-foreground">llama-3.3-70b-versatile</td>
              </tr>
              <tr>
                <td className="py-2 pr-4 font-mono text-cyan-400">LEARNLOCK_GEMINI_MODEL</td>
                <td className="py-2 pr-4 font-mono text-muted-foreground">gemini-2.5-flash</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Spaced Repetition (SM-2)</h2>
        <div className="-mx-2 px-2 sm:mx-0 sm:px-0 overflow-x-auto">
          <table className="w-full text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-4 text-muted-foreground">Variable</th>
                <th className="text-left py-2 pr-4 text-muted-foreground">Default</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4 font-mono text-cyan-400">LEARNLOCK_SM2_INITIAL_EASE</td>
                <td className="py-2 pr-4 font-mono text-muted-foreground">2.5</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4 font-mono text-cyan-400">LEARNLOCK_SM2_INITIAL_INTERVAL</td>
                <td className="py-2 pr-4 font-mono text-muted-foreground">1.0</td>
              </tr>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4 font-mono text-cyan-400">LEARNLOCK_SM2_MIN_EASE</td>
                <td className="py-2 pr-4 font-mono text-muted-foreground">1.3</td>
              </tr>
              <tr>
                <td className="py-2 pr-4 font-mono text-cyan-400">LEARNLOCK_SM2_MAX_INTERVAL</td>
                <td className="py-2 pr-4 font-mono text-muted-foreground">180</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Grading</h2>
        <div className="-mx-2 px-2 sm:mx-0 sm:px-0 overflow-x-auto">
          <table className="w-full text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-4 text-muted-foreground">Variable</th>
                <th className="text-left py-2 pr-4 text-muted-foreground">Default</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-border/50">
                <td className="py-2 pr-4 font-mono text-cyan-400">LEARNLOCK_SCORE_PASS_THRESHOLD</td>
                <td className="py-2 pr-4 font-mono text-muted-foreground">3</td>
              </tr>
              <tr>
                <td className="py-2 pr-4 font-mono text-cyan-400">LEARNLOCK_DEFAULT_FALLBACK_SCORE</td>
                <td className="py-2 pr-4 font-mono text-muted-foreground">3</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Example Setup</h2>
        <pre className="bg-card p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`# ~/.bashrc or ~/.zshrc

# Required
export GROQ_API_KEY="gsk_..."
export GEMINI_API_KEY="AI..."

# Optional
export LEARNLOCK_DATA_DIR="$HOME/Documents/learnlock"
export LEARNLOCK_SM2_MAX_INTERVAL=365`}</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Data Location</h2>
        <pre className="bg-card p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`~/.learnlock/
  data.db    # SQLite database`}</code></pre>
        <p className="text-xs sm:text-sm text-muted-foreground mt-2">
          To backup: copy data.db. To reset: delete it.
        </p>
      </section>

      <div className="p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
        <p className="text-xs sm:text-sm text-muted-foreground mb-2">Back to:</p>
        <Link href="/docs" className="inline-flex items-center gap-2 text-sm sm:text-base text-foreground hover:underline font-medium">
          Documentation Overview
        </Link>
      </div>
    </div>
  );
}
