# learnlock

**Stop consuming. Start retaining.**

A CLI tool that extracts concepts from content, quizzes you with active recall challenges, grades your explanations using AI, and schedules reviews with spaced repetition.

---

## What It Actually Does

1. **Add content** — YouTube videos, articles, PDFs, GitHub repos
2. **Extract concepts** — LLM identifies 8-12 key concepts with challenge questions
3. **Quiz you** — Forces you to explain concepts in your own words
4. **Grade explanations** — AI evaluates against source material
5. **Schedule reviews** — SM-2 algorithm brings concepts back at optimal intervals

That's it. No knowledge graphs. No micro-projects. No magic.

---

## Quick Start

```bash
# Install
pip install learnlock

# Set API key (free tier works)
export GROQ_API_KEY=your_key_from_console.groq.com

# Optional: Better evaluation quality
export GEMINI_API_KEY=your_key_from_aistudio.google.com

# Run
learnlock
```

---

## Usage

```
learnlock

██╗     ███████╗ █████╗ ██████╗ ███╗   ██╗██╗      ██████╗  ██████╗██╗  ██╗
██║     ██╔════╝██╔══██╗██╔══██╗████╗  ██║██║     ██╔═══██╗██╔════╝██║ ██╔╝
██║     █████╗  ███████║██████╔╝██╔██╗ ██║██║     ██║   ██║██║     █████╔╝ 
██║     ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║██║     ██║   ██║██║     ██╔═██╗ 
███████╗███████╗██║  ██║██║  ██║██║ ╚████║███████╗╚██████╔╝╚██████╗██║  ██╗
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝

Commands:
  /add <source>     Add YouTube, article, GitHub, or PDF
  /study            Study due concepts
  /stats            Show your progress
  /list             List all concepts
  /due              Show what's due
  /skip <name>      Skip a concept permanently
  /unskip <name>    Restore skipped concept
  /help             Show help
  /quit             Exit
```

### Adding Content

```bash
# YouTube (extracts transcript)
learnlock> https://youtube.com/watch?v=dQw4w9WgXcQ

# Article
learnlock> https://example.com/blog/some-article

# GitHub repo (extracts README)
learnlock> https://github.com/user/repo

# PDF (local or URL)
learnlock> /path/to/document.pdf
learnlock> https://example.com/paper.pdf
```

### Studying

```
learnlock> /study

📚 Study Session — 5 concepts to review

━━━ 1/5: Attention Mechanism ━━━
from Transformer Architecture Explained

Challenge: What problem does the attention mechanism solve in sequence models?

Hint: "Attention allows the model to focus on relevant parts..."

(Press Enter twice when done)
> Attention solves the problem of fixed-length context in RNNs.
  It lets the model look at all input positions when generating
  each output, weighted by relevance.

★★★★☆ Great
Good coverage of the core concept.
✓ You got:
  • fixed context problem
  • weighted relevance
✗ You missed:
  • parallel computation benefit

📅 Next review: in 3 days
```

---

## Supported Sources

| Source | Method | Notes |
|--------|--------|-------|
| YouTube | Transcript API | Falls back to Whisper if no captions |
| Articles | trafilatura | Works on most blogs, may fail on paywalls |
| PDF | pymupdf | Text extraction only, no OCR |
| GitHub | API | Extracts README only |

---

## How Grading Works

Your explanation is evaluated against the source material:

| Score | Meaning |
|-------|---------|
| ★★★★★ | Perfect — Covered all key points |
| ★★★★☆ | Great — Minor gaps |
| ★★★☆☆ | Good — Partial understanding |
| ★★☆☆☆ | Getting There — Significant gaps |
| ★☆☆☆☆ | Needs Work — Review the source |

Scores ≥3 advance the concept. Scores <3 reset the interval.

---

## Spaced Repetition

Uses the SM-2 algorithm:
- New concepts are due immediately
- Correct answers increase interval (1 day → 3 days → 1 week → 2 weeks → ...)
- Wrong answers reset to 1 day
- "Mastered" = 3+ reviews with ease factor ≥2.5

---

## Data Storage

All data stored locally in `~/.learnlock/data.db` (SQLite).

No cloud sync. No accounts. No telemetry.

---

## Configuration

Set via environment variables:

```bash
# Required
GROQ_API_KEY=your_key

# Optional
GEMINI_API_KEY=your_key              # Better evaluation quality
LEARNLOCK_DATA_DIR=~/.learnlock      # Data directory
LEARNLOCK_MIN_CONCEPTS=8             # Min concepts per source
LEARNLOCK_MAX_CONCEPTS=12            # Max concepts per source
```

---

## Limitations

Be honest about what this doesn't do:

- **No mobile app** — CLI only
- **No sync** — Local SQLite, single device
- **No OCR** — Scanned PDFs won't work
- **No timestamps** — Can't link back to video timestamps
- **No knowledge graph** — Concepts aren't connected
- **No team features** — Single user only
- **Requires API keys** — No offline mode

---

## Tech Stack

- Python 3.11+
- SQLite (local storage)
- Groq API (concept extraction via Llama)
- Gemini API (evaluation, optional)
- typer + rich (CLI)
- trafilatura (article extraction)
- youtube-transcript-api
- pymupdf (PDF extraction)

---

## Development

```bash
# Clone
git clone https://github.com/MitudruDutta/learnlock.git
cd learnlock

# Install in dev mode
pip install -e ".[dev]"

# Run
learnlock
```

---

## License

MIT

---

## Why This Exists

I kept watching YouTube tutorials and forgetting everything. Anki is tedious. ChatGPT doesn't track progress. This scratches my own itch.

If it helps you too, cool. If not, there are better tools with actual funding and mobile apps.
