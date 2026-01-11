```
██╗     ███████╗ █████╗ ██████╗ ███╗   ██╗██╗      ██████╗  ██████╗██╗  ██╗
██║     ██╔════╝██╔══██╗██╔══██╗████╗  ██║██║     ██╔═══██╗██╔════╝██║ ██╔╝
██║     █████╗  ███████║██████╔╝██╔██╗ ██║██║     ██║   ██║██║     █████╔╝ 
██║     ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║██║     ██║   ██║██║     ██╔═██╗ 
███████╗███████╗██║  ██║██║  ██║██║ ╚████║███████╗╚██████╔╝╚██████╗██║  ██╗
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝
```

> **The app that argues with you.**

A CLI tool that uses adversarial Socratic dialogue to expose gaps in your understanding. It won't let you bullshit your way through learning.

```
> Attention helps focus on important things.

 That's vague. WHY is focusing necessary? What problem did older models have?

> I don't know.

██░░░ Gaps exposed: bottleneck problem, Q/K/V mechanism
```

---

## Installation

### pip (all platforms)
```bash
pip install learnlock
```

### curl (macOS/Linux)
```bash
curl -fsSL https://raw.githubusercontent.com/MitudruDutta/learnlock/main/install.sh | bash
```

### From source
```bash
git clone https://github.com/MitudruDutta/learnlock.git
cd learnlock
pip install -e .
```

---

## Setup

```bash
# Required (free at console.groq.com)
export GROQ_API_KEY=your_key

# Recommended (free at aistudio.google.com)
export GEMINI_API_KEY=your_key
```

**Windows:**
```powershell
$env:GROQ_API_KEY="your_key"
$env:GEMINI_API_KEY="your_key"
```

---

## Usage

```bash
learnlock
```

```
██╗     ███████╗ █████╗ ██████╗ ███╗   ██╗██╗      ██████╗  ██████╗██╗  ██╗
██║     ██╔════╝██╔══██╗██╔══██╗████╗  ██║██║     ██╔═══██╗██╔════╝██║ ██╔╝
██║     █████╗  ███████║██████╔╝██╔██╗ ██║██║     ██║   ██║██║     █████╔╝ 
██║     ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║██║     ██║   ██║██║     ██╔═██╗ 
███████╗███████╗██║  ██║██║  ██║██║ ╚████║███████╗╚██████╔╝╚██████╗██║  ██╗
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝
The app that argues with you
```

**Add content:**
```
learnlock> https://youtube.com/watch?v=...
learnlock> https://github.com/user/repo
learnlock> /path/to/file.pdf
```

**Study:**
```
learnlock> /study
```

---

## How It Works

1. **Add** — YouTube, articles, PDFs, GitHub READMEs
2. **Extract** — LLM identifies 8-12 key concepts
3. **Challenge** — You explain, it finds holes
4. **Probe** — Up to 3 rounds of Socratic follow-ups
5. **Score** — Based on gaps exposed
6. **Repeat** — SM-2 brings weak concepts back

---

## Commands

| Command | Description |
|---------|-------------|
| `/add <url>` | Add content |
| `/study` | Start session |
| `/stats` | View progress |
| `/list` | List concepts |
| `/due` | What's due |
| `/skip <name>` | Skip concept |
| `/help` | All commands |

---

## Features

- **Adversarial Socratic dialogue** — Challenges vague answers
- **Multi-source support** — YouTube, articles, PDFs, GitHub
- **OCR for images** — Answer with handwritten notes
- **Spaced repetition** — SM-2 algorithm
- **Local storage** — SQLite, no cloud, no telemetry

---

## Optional: OCR Support

For image-based answers:
```bash
pip install learnlock[ocr]
```

---

## Requirements

- Python 3.11+
- GROQ_API_KEY (free at [console.groq.com](https://console.groq.com))
- GEMINI_API_KEY (optional, free at [aistudio.google.com](https://aistudio.google.com))

---

## License

MIT

---

<p align="center"><b>Stop consuming. Start retaining.</b></p>
