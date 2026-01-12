# LearnLock Docs

Documentation site for LearnLock. Built with Next.js 16, Tailwind v4, Framer Motion.

## Stack

- Next.js 16 (App Router)
- Tailwind CSS 4
- Framer Motion
- Radix UI
- Lucide Icons

## Run

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Structure

```
src/
├── app/
│   ├── docs/           # Doc pages
│   └── page.tsx        # Landing
├── components/
│   ├── blocks/         # Navbar, Hero
│   ├── landing/        # TerminalDemo
│   └── ui/             # Buttons, Cards, etc.
└── lib/                # Utils, nav config
```

## Features

- Glassmorphism navbar (sticky, backdrop-blur)
- Interactive terminal demo (full duel flow)
- Infinite scrolling feature cards
- Lamp effect hero
- PixelCanvas hover effects
- Zinc palette (#18181b base)
- Mobile responsive

## Pages

- `/` — Landing
- `/docs` — Introduction
- `/docs/installation`
- `/docs/quickstart`
- `/docs/adversarial-learning`
- `/docs/socratic-dialogue`
- `/docs/spaced-repetition`
- `/docs/duel-engine`
- `/docs/commands`
- `/docs/adding-content`
- `/docs/study-sessions`
- `/docs/ocr`
- `/docs/configuration`

---

[learnlock.vercel.app](https://learnlock.vercel.app)
