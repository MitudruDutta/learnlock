"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";

const COMMANDS = [
  ["/add <source>", "Add a YouTube video, article, GitHub repo, or PDF path/URL."],
  ["/study", "Start the current due session. Press Enter on an empty prompt as a shortcut."],
  ["/stats", "Show sources, concepts, due count, review stats, and mastery progress."],
  ["/list", "List active concepts grouped by source."],
  ["/due", "Show what is currently due for review."],
  ["/skip <name-or-id>", "Skip a concept during normal review rotation."],
  ["/unskip <name-or-id>", "Restore a skipped concept."],
  ["/claims <name-or-id>", "View, generate, edit, or delete cached claims for a concept."],
  ["/delete <source-or-id>", "Delete a source and all associated concepts after confirmation."],
  ["/export [file]", "Export a versioned JSON backup. Supports paths like ~/learnlock-export.json."],
  ["/import <file>", "Validate and merge a JSON backup into the current database."],
  ["/visual [name-or-id]", "On-demand YouTube frame inspection for the last reviewed or selected concept."],
  ["/config", "Show the active data path, models, and API key availability."],
  ["/clear", "Clear the screen and re-render the LearnLock banner."],
  ["/help", "Show the built-in help text."],
  ["/quit", "Exit LearnLock."],
];

const FLAGS = [
  ["--gentle, -g", "Force the softer HUD and supportive feedback mode."],
  ["--version, -v", "Print the installed LearnLock version and exit."],
];

export default function CommandsPage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight mb-3 sm:mb-4">
          CLI Commands
        </h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground">
          Complete reference for the v0.1.7 command surface.
        </p>
      </div>

      <section className="rounded-xl border border-[#3f3f46] bg-[#1f1f23] p-4 sm:p-5">
        <p className="text-xs sm:text-sm uppercase tracking-[0.2em] text-[#71717a]">
          Release Notes
        </p>
        <h2 className="mt-2 text-lg sm:text-xl font-semibold text-white">
          Phase 3 commands are now documented.
        </h2>
        <p className="mt-2 text-sm sm:text-base text-muted-foreground">
          The CLI now supports claim review, source deletion, versioned export/import
          merging, and opt-in YouTube visual inspection. The docs below match the
          current shipped behavior rather than the older pre-Phase 3 flow.
        </p>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Command Overview</h2>
        <div className="overflow-x-auto -mx-2 px-2 sm:mx-0 sm:px-0">
          <table className="w-full text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-3 sm:pr-4 text-muted-foreground">
                  Command
                </th>
                <th className="text-left py-2 text-muted-foreground">Description</th>
              </tr>
            </thead>
            <tbody>
              {COMMANDS.map(([command, description]) => (
                <tr key={command} className="border-b border-border/50 last:border-0">
                  <td className="py-2 pr-3 sm:pr-4 font-mono text-cyan-400 whitespace-nowrap">
                    {command}
                  </td>
                  <td className="py-2">{description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">High-Leverage Workflows</h2>

        <div className="space-y-4">
          <div>
            <h3 className="text-base sm:text-lg font-medium">Add and Study</h3>
            <pre className="bg-[#1f1f23] border border-[#3f3f46] p-4 rounded-lg overflow-x-auto text-xs sm:text-sm">
              <code>{`learnlock> /add https://youtu.be/kCc8FmEb1nY
learnlock> /study

Type 'skip' to skip, 'q' to quit.
Press Enter twice to submit each answer.`}</code>
            </pre>
          </div>

          <div>
            <h3 className="text-base sm:text-lg font-medium">Review or Fix Claims Before Studying</h3>
            <pre className="bg-[#1f1f23] border border-[#3f3f46] p-4 rounded-lg overflow-x-auto text-xs sm:text-sm">
              <code>{`learnlock> /claims 12

edit 2 Attention weights come from the query-key dot product.
delete 4
done`}</code>
            </pre>
            <p className="mt-2 text-xs sm:text-sm text-muted-foreground">
              You can target concepts by name or numeric id. If claims do not exist yet,
              LearnLock now generates them on demand.
            </p>
          </div>

          <div>
            <h3 className="text-base sm:text-lg font-medium">Safe Backup and Merge</h3>
            <pre className="bg-[#1f1f23] border border-[#3f3f46] p-4 rounded-lg overflow-x-auto text-xs sm:text-sm">
              <code>{`learnlock> /export ~/learnlock-backup.json
learnlock> /import ~/learnlock-backup.json`}</code>
            </pre>
            <p className="mt-2 text-xs sm:text-sm text-muted-foreground">
              Imports are validated before touching the database and merge existing
              sources, concepts, progress, duel memory, and cached claims.
            </p>
          </div>

          <div>
            <h3 className="text-base sm:text-lg font-medium">Inspect the Visual Context</h3>
            <pre className="bg-[#1f1f23] border border-[#3f3f46] p-4 rounded-lg overflow-x-auto text-xs sm:text-sm">
              <code>{`learnlock> /visual
# or target a concept directly
learnlock> /visual 18`}</code>
            </pre>
            <p className="mt-2 text-xs sm:text-sm text-muted-foreground">
              <code className="bg-[#1f1f23] px-1 rounded">/visual</code> is opt-in and only
              applies to YouTube concepts with transcript timestamps. It uses Gemini Vision
              to describe the linked frame.
            </p>
          </div>
        </div>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Flags</h2>
        <div className="-mx-2 px-2 sm:mx-0 sm:px-0 overflow-x-auto">
          <table className="w-full text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-4 text-muted-foreground">Flag</th>
                <th className="text-left py-2 text-muted-foreground">Description</th>
              </tr>
            </thead>
            <tbody>
              {FLAGS.map(([flag, description]) => (
                <tr key={flag} className="border-b border-border/50 last:border-0">
                  <td className="py-2 pr-4 font-mono text-cyan-400">{flag}</td>
                  <td className="py-2">{description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs sm:text-sm text-muted-foreground mt-2">
          New installs start in gentle mode automatically until you have 5 successful
          reviews. Use <code className="bg-[#1f1f23] px-1 rounded">--gentle</code> to force
          that mode even after you graduate to the full HUD.
        </p>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Aliases</h2>
        <ul className="list-disc list-inside space-y-1 text-xs sm:text-sm text-muted-foreground">
          <li>
            <code className="bg-[#1f1f23] px-1 rounded">/list</code> also works as{" "}
            <code className="bg-[#1f1f23] px-1 rounded">/ls</code>.
          </li>
          <li>
            <code className="bg-[#1f1f23] px-1 rounded">/help</code> also works as{" "}
            <code className="bg-[#1f1f23] px-1 rounded">/h</code> and{" "}
            <code className="bg-[#1f1f23] px-1 rounded">/?</code>.
          </li>
          <li>
            <code className="bg-[#1f1f23] px-1 rounded">/clear</code> also works as{" "}
            <code className="bg-[#1f1f23] px-1 rounded">/cls</code>.
          </li>
          <li>
            <code className="bg-[#1f1f23] px-1 rounded">/quit</code> also works as{" "}
            <code className="bg-[#1f1f23] px-1 rounded">/exit</code> and{" "}
            <code className="bg-[#1f1f23] px-1 rounded">/q</code>.
          </li>
        </ul>
      </section>

      <div className="p-3 sm:p-4 rounded-lg border border-[#3f3f46] bg-[#1f1f23]">
        <p className="text-xs sm:text-sm text-muted-foreground mb-2">Next:</p>
        <Link
          href="/docs/study-sessions"
          className="inline-flex items-center gap-2 text-sm sm:text-base text-foreground hover:underline font-medium"
        >
          Study Sessions <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
