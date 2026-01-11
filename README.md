# learn-lock

**Stop consuming. Start retaining.**

learn-lock is a learning accountability system that forces active recall, grades your understanding, and haunts you with spaced repetition until you actually know the material.

---

## The Problem

You watch a 30-minute video. You think you understood it. A week later, you remember nothing.

- Passive consumption doesn't work
- Flashcard apps are boring and you stop using them
- There's no feedback loop telling you what you actually missed

## The Solution

learn-lock extracts concepts from any content (YouTube, articles, PDFs), generates challenges that force you to explain concepts in your own words, grades your explanations against the source material, and schedules spaced repetition reviews.

**You either prove you understood, or learn-lock exposes that you didn't.**

---

## How It Works

```bash
# Add content
$ learnlock add "https://youtube.com/watch?v=attention-explained"
✓ Extracted 8 concepts from "Attention Is All You Need Explained"
✓ Generated 8 challenges, 3 micro-projects
✓ Scheduled first review for tomorrow

# Study (when concepts are due)
$ learnlock study

📚 Concept: Attention Mechanism

Challenge: Explain why attention uses Q, K, V matrices instead of a single matrix.

Your explanation: > The Q, K, V matrices allow the model to learn different 
                    representations for querying, matching, and retrieving...

Score: 72/100

✓ Covered: Q/K/V separation, dot product similarity
✗ Missed: Scaling factor (sqrt(d_k)) — Review at timestamp 14:32
✗ Missed: Why scaling prevents gradient issues

Next review: 2 days

# Track progress
$ learnlock stats
Concepts learned: 47
Retention rate: 78%
Streak: 5 days
Weakest area: "Mathematical foundations" (62% retention)
```

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Multi-source ingestion** | YouTube, articles, PDFs, markdown notes, GitHub repos |
| **Concept extraction** | Identifies key concepts with difficulty ratings and prerequisites |
| **Active recall challenges** | "Explain X", "Compare X and Y", "Apply X to solve Y" |
| **Rubric-based grading** | Grades against what the source actually said, not vibes |
| **Source citations** | Points to exact timestamps/paragraphs when you're wrong |
| **Spaced repetition** | SM-2 algorithm schedules reviews at optimal intervals |
| **Knowledge graph** | Connects concepts across sources, finds relationships |
| **Micro-projects** | Suggests builds that reinforce what you learned |
| **Progress tracking** | Retention stats, streaks, weak area identification |

---

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [User Flow](docs/USER_FLOW.md)
- [System Design](docs/SYSTEM_DESIGN.md)
- [Data Models](docs/DATA_MODELS.md)
- [Grading System](docs/GRADING.md)
- [Spaced Repetition](docs/SPACED_REPETITION.md)
- [Build Plan](docs/BUILD_PLAN.md)

---

## Quick Start

```bash
# Install
pip install learn-lock

# Configure LLM
export GEMINI_API_KEY=your_key

# Add your first content
learnlock add "https://youtube.com/watch?v=your-video"

# Start studying
learnlock study
```

---

## Why This Isn't Just Another Flashcard App

| Flashcard Apps | learn-lock |
|----------------|------------|
| Passive Q&A | Active explanation challenges |
| No feedback on wrong answers | Rubric-based grading with specific feedback |
| No source connection | Points to exact source location |
| Isolated cards | Knowledge graph connects concepts |
| You create cards manually | Auto-extracts from any content |
| No projects | Generates micro-projects to apply learning |

---

## Tech Stack

- Python 3.11+
- SQLite (knowledge base)
- Gemini API (LLM)
- youtube-transcript-api
- trafilatura (article extraction)
- typer (CLI)

---

## License

MIT
