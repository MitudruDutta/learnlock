```
██╗     ███████╗ █████╗ ██████╗ ███╗   ██╗██╗      ██████╗  ██████╗██╗  ██╗
██║     ██╔════╝██╔══██╗██╔══██╗████╗  ██║██║     ██╔═══██╗██╔════╝██║ ██╔╝
██║     █████╗  ███████║██████╔╝██╔██╗ ██║██║     ██║   ██║██║     █████╔╝
██║     ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║██║     ██║   ██║██║     ██╔═██╗
███████╗███████╗██║  ██║██║  ██║██║ ╚████║███████╗╚██████╔╝╚██████╗██║  ██╗
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝
```

> **The app that argues with you.**

[![PyPI version](https://img.shields.io/pypi/v/learn-lock)](https://pypi.org/project/learn-lock/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/MitudruDutta/learnlock/actions/workflows/test.yml/badge.svg)](https://github.com/MitudruDutta/learnlock/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

LearnLock is a CLI learning tool that uses adversarial Socratic dialogue to expose gaps in your understanding. It doesn't quiz you — it _interrogates_ you.

Feed it a YouTube video, article, PDF, or GitHub repo. It extracts concepts, builds falsifiable claims, then duels you — inferring what you believe, finding contradictions, and attacking your weakest points.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [The Duel Engine](#the-duel-engine)
- [Claim Pipeline](#claim-pipeline)
- [CLI Commands](#cli-commands)
- [Configuration](#configuration)
- [Development](#development)
- [Known Limitations](#known-limitations)
- [License](#license)

---

## Installation

### From PyPI

```bash
pip install learn-lock==0.1.6
```

Requires Python 3.11 or higher.

### From Source

```bash
git clone https://github.com/MitudruDutta/learnlock.git
cd learnlock
pip install -e ".[dev]"
```

### Optional Dependencies

```bash
pip install "learn-lock[ocr]"      # EasyOCR for handwritten answer support
pip install "learn-lock[whisper]"   # Whisper fallback for YouTube without transcripts
```

---

## Quick Start

1. Set at least one API key:

```bash
export GROQ_API_KEY=your_key        # Fast extraction + fallback calls
export GEMINI_API_KEY=your_key      # Better duel evaluation + /visual
```

Or create a `.env` file in the project root.

2. Launch:

```bash
learnlock
```

3. Paste a YouTube URL, article link, PDF path, or GitHub repo URL

4. Start studying with `/study` or just press Enter on an empty prompt

5. Double Enter to send your answer

6. New users start in gentle mode automatically until they reach 5 successful reviews

---

## How It Works

1. You explain a concept in your own words
2. The engine infers what you believe
3. It compares your belief against cached ground truth claims
4. It finds contradictions, weighs their confidence, and attacks the strongest actionable point
5. After 3 turns (or success), it reveals your belief trajectory
6. Your score feeds into SM-2 spaced repetition scheduling

---

## Architecture

```
Source (YouTube/PDF/Article/GitHub)
    │
    ▼
Content Extraction (tools/)
    │
    ▼
Concept Extraction (llm.py) ──▶ 8-12 concepts with claims
    │
    ▼
Storage (SQLite + WAL) ──▶ sources, concepts, progress, duel_memory, cached_claims
    │
    ▼
Scheduler (SM-2) ──▶ spaced repetition with ease factor + interval
    │
    ▼
Duel Engine (duel.py) ──▶ belief modeling → contradiction detection → interrogation
    │
    ▼
HUD (hud.py) ──▶ Rich TUI with claims, belief state, attack panels
```

### LLM Pipeline

- **Groq** — fast inference for concept extraction and title generation
- **Gemini** — quality inference for duel evaluation and vision
- Centralized `llm.call()` with retry, exponential backoff, and automatic provider fallback
- Per-provider rate limiting (token bucket)
- Input sanitization before prompt interpolation

---

## The Duel Engine

The cognitive core. Located in `duel.py`.

### Philosophy

Traditional learning apps ask: "Do you know X?"

LearnLock asks: "What do you _believe_ about X, and where is it wrong?"

### Pipeline

1. **Belief Modeling** — Infers what the user thinks from their response
2. **Contradiction Detection** — Compares belief against claims, finds violations
3. **Interrogation** — Generates attack question targeting highest-severity error
4. **Snapshot** — Records belief state for trajectory tracking

### Behaviors

- Vague answers trigger mechanism probes
- Wrong answers trigger claim-specific attacks
- "I don't know" triggers guiding questions (not punishment)
- Low-confidence errors can be shown without tanking the final score
- Correct answers pass after verification
- 3 turns exhausted triggers reveal with full trajectory

### Graded Harshness

- Turn 1: Forgiving — only clear violations flagged
- Turn 2: Moderate — violations plus omissions
- Turn 3: Strict — all violations surfaced

### Error Types

| Type | Description |
|------|-------------|
| `wrong_mechanism` | Incorrect explanation of how something works |
| `missing_mechanism` | Omitted critical mechanism |
| `boundary_error` | Wrong about limitations or scope |
| `conflation` | Confused two distinct concepts |
| `superficial` | Surface-level understanding without depth |

---

## Claim Pipeline

Claims are the epistemic foundation. The duel is only as fair as the claims.

### Three-Pass Verification

**Pass 1: Generation** — LLM generates claims with explicit instructions to produce conceptual truths, not transcript parroting. Demands falsifiable statements about WHY and HOW, not just WHAT.

**Pass 2: Garbage Filter** — Pattern matching rejects stateful claims ("is running", "must remain active"), tautologies ("processes requests", "serves requests"), and vague claims ("is useful", "is important").

**Pass 3: Sharpness Filter** — Rejects blurry truths that are technically correct but unfalsifiable ("handles security", "manages data", "deals with").

### Claim Types

| Type | Purpose |
|------|---------|
| `definition` | What the concept is |
| `mechanism` | How it works internally |
| `requirement` | What it needs to function |
| `boundary` | What it cannot do or where it fails |

### Claim Caching

Claims are generated lazily on first duel or the first `/claims` request, then cached in the database (`cached_claims` table). Subsequent duels and claim reviews load from cache instead of re-parsing, making study sessions faster and more deterministic.

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `/add <url>` | Add YouTube, article, PDF, or GitHub |
| `/study` | Start duel session |
| `/stats` | View progress statistics |
| `/list` | List all concepts |
| `/due` | Show concepts due for review |
| `/skip <name>` | Skip a concept |
| `/unskip <name>` | Restore skipped concept |
| `/claims <name-or-id>` | View, generate, edit, or delete cached claims |
| `/delete <source-or-id>` | Delete a source and all related concepts |
| `/export [file]` | Export a versioned JSON backup |
| `/import <file>` | Validate and merge a JSON backup |
| `/visual [name-or-id]` | Inspect the linked YouTube frame on demand |
| `/config` | Show current configuration |
| `/help` | Show help |
| `/quit` | Exit |

### Flags

| Flag | Description |
|------|-------------|
| `-g`, `--gentle` | Gentle UI mode (supportive feedback) |
| `-v`, `--version` | Show version |
| `-p`, `--print` | Print output and exit (non-interactive) |

Notes:
- New installs automatically start in gentle mode until 5 successful reviews are recorded.
- `/claims`, `/delete`, and `/visual` accept numeric IDs to resolve ambiguous names.
- `/visual` is opt-in and only applies to YouTube concepts with timestamped transcript matches.

---

## Configuration

All settings via environment variables or `.env` file.

### API Keys

| Variable | Required | Source |
|----------|----------|--------|
| `GROQ_API_KEY` | One of `GROQ_API_KEY` or `GEMINI_API_KEY` is required | [console.groq.com](https://console.groq.com) |
| `GEMINI_API_KEY` | Recommended | [aistudio.google.com](https://aistudio.google.com) |

### Models

| Variable | Default |
|----------|---------|
| `LEARNLOCK_GROQ_MODEL` | `openai/gpt-oss-120b` |
| `LEARNLOCK_GEMINI_MODEL` | `gemini-2.0-flash` |

### SM-2 Parameters

| Variable | Default | Description |
|----------|---------|-------------|
| `LEARNLOCK_SM2_INITIAL_EASE` | `2.5` | Starting ease factor |
| `LEARNLOCK_SM2_INITIAL_INTERVAL` | `1.0` | Starting interval (days) |
| `LEARNLOCK_SM2_MIN_EASE` | `1.3` | Minimum ease factor |
| `LEARNLOCK_SM2_MAX_INTERVAL` | `180` | Maximum interval (days) |

### Extraction

| Variable | Default | Description |
|----------|---------|-------------|
| `LEARNLOCK_MIN_CONCEPTS` | `8` | Min concepts per source |
| `LEARNLOCK_MAX_CONCEPTS` | `12` | Max concepts per source |
| `LEARNLOCK_CONTENT_MAX_CHARS` | `8000` | Max content length |

### LLM Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `LEARNLOCK_LLM_MIN_CALL_INTERVAL` | `0.5` | Min seconds between LLM calls |
| `LEARNLOCK_LLM_MAX_RETRIES` | `2` | Max retries per provider |
| `LEARNLOCK_LLM_BACKOFF_BASE` | `1.0` | Exponential backoff base (seconds) |

---

## Development

### Setup

```bash
git clone https://github.com/MitudruDutta/learnlock.git
cd learnlock
pip install -e ".[dev]"
```

### Testing

```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/test_duel.py # Run specific test file
```

### Linting

```bash
ruff check src tests
```

### Building

```bash
python -m build
python -m twine check dist/*
```

### Project Structure

```
src/learnlock/
├── __init__.py      # Version from importlib.metadata
├── cli.py           # CLI interface and command routing
├── config.py        # Environment-based configuration with validation
├── duel.py          # Duel Engine — belief modeling, contradiction, interrogation
├── hud.py           # Rich TUI — claims, belief, attack, reveal panels
├── llm.py           # LLM interface — call(), retry, fallback, sanitization
├── ocr.py           # Image text extraction (EasyOCR/Tesseract)
├── scheduler.py     # SM-2 spaced repetition
├── security.py      # URL validation, filename sanitization, safe redirects
├── storage.py       # SQLite persistence with lazy init and claim caching
├── py.typed         # PEP 561 type marker
└── tools/
    ├── __init__.py
    ├── youtube.py   # YouTube transcript + timestamp extraction
    ├── article.py   # Web article extraction (trafilatura)
    ├── pdf.py       # PDF extraction (pymupdf)
    └── github.py    # GitHub README extraction
tests/
├── conftest.py      # Fixtures: tmp_db, mock_llm, seeded_db
├── test_cli.py      # CLI command routing and input detection
├── test_duel.py     # Duel engine, belief scoring, claim verification
├── test_llm.py      # JSON parsing, sanitization, concept extraction
├── test_scheduler.py # SM-2 algorithm, due queries, intervals
├── test_storage.py  # All CRUD ops, migrations, caching
└── test_tools.py    # YouTube URL normalization, timestamp search
```

---

## Known Limitations

### Claim Quality (Epistemic Risk)

Claims are LLM-generated. Despite three-pass filtering, semantic drift can occur — a source saying "enforces authentication" might become "handles security." Pattern filters reduce but don't eliminate this.

### Hallucinated Errors (Moral Risk)

The contradiction detector can still invent violations. A correct answer might be flagged as `missing_mechanism` due to LLM drift. Graded harshness, claim-index validation, and confidence weighting mitigate but do not eliminate this.

### Confidence Is Not Full Verification

The engine can now express low-confidence findings and down-weight them before scoring, but this is still single-pass judgment. It is not the same as multi-pass agreement or formal claim verification.

### Import/Export Is Merge-Oriented, Not Multi-Device Sync

`/export` and `/import` are safe for backup, restore, and controlled merges. They are not yet a full conflict-free sync protocol for multiple machines writing concurrently.

### UI Density

The full HUD shows claims, belief, attack target, and interrogation simultaneously. LearnLock starts new users in gentle mode automatically, and `--gentle` can keep that softer experience enabled later.

---

## License

MIT

---

<p align="center">
<b>Stop consuming. Start retaining.</b>
<br><br>
LearnLock doesn't teach you.<br>
It finds out what you don't know.
</p>
