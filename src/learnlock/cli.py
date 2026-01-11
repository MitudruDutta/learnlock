"""learn-lock CLI - Interactive learning system like Claude Code."""

import sys
import os
import json
import re
import select
import warnings
import logging

# Suppress all warnings and litellm logging noise
warnings.filterwarnings("ignore")
logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
logging.getLogger("litellm").setLevel(logging.CRITICAL)

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Callable

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box

from . import config
from . import storage
from . import scheduler
from . import llm
from .tools import extract_youtube, extract_article, extract_pdf, extract_github


def _flush_stdin():
    """Flush any buffered stdin input."""
    if sys.platform == "win32":
        try:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        except:
            pass
    else:
        try:
            import termios
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
        except:
            try:
                while select.select([sys.stdin], [], [], 0)[0]:
                    sys.stdin.readline()
            except:
                pass

# ============ CONSTANTS ============
VERSION = "0.1.0"
BANNER = """[bold cyan]
██╗     ███████╗ █████╗ ██████╗ ███╗   ██╗██╗      ██████╗  ██████╗██╗  ██╗
██║     ██╔════╝██╔══██╗██╔══██╗████╗  ██║██║     ██╔═══██╗██╔════╝██║ ██╔╝
██║     █████╗  ███████║██████╔╝██╔██╗ ██║██║     ██║   ██║██║     █████╔╝ 
██║     ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║██║     ██║   ██║██║     ██╔═██╗ 
███████╗███████╗██║  ██║██║  ██║██║ ╚████║███████╗╚██████╔╝╚██████╗██║  ██╗
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝[/bold cyan]
"""

HELP_TEXT = """
[bold]Commands:[/bold]
  [cyan]/add[/cyan] <source>     Add YouTube, article, GitHub, or PDF
  [cyan]/study[/cyan]            Start adversarial study session
  [cyan]/stats[/cyan]            Show your progress
  [cyan]/list[/cyan]             List all concepts
  [cyan]/due[/cyan]              Show what's due
  [cyan]/skip[/cyan] <name>      Skip a concept
  [cyan]/unskip[/cyan] <name>    Restore skipped concept
  [cyan]/config[/cyan]           Show configuration
  [cyan]/clear[/cyan]            Clear screen
  [cyan]/help[/cyan]             Show this help
  [cyan]/quit[/cyan]             Exit

[bold]How It Works:[/bold]
  1. You explain a concept
  2. I find holes in your understanding
  3. I challenge you with follow-up questions
  4. Your score drops for each gap exposed
  5. No bullshitting allowed

[bold]Supported Sources:[/bold]
  • YouTube videos • GitHub repos • PDFs • Web articles

[bold]Tips:[/bold]
  • Paste a URL to add content
  • Press Enter to start studying
  • Be specific — vague answers get challenged
"""

console = Console()
app = typer.Typer(no_args_is_help=False)


# ============ UTILITIES ============

def _spinner(msg: str):
    return Progress(
        SpinnerColumn(style="cyan"),
        TextColumn(f"[dim]{msg}[/dim]"),
        transient=True,
        console=console,
    )


def _is_url(text: str) -> bool:
    return text.startswith(("http://", "https://", "www."))


def _is_local_file(text: str) -> bool:
    return os.path.exists(text)


def _is_image_path(text: str) -> bool:
    """Check if text is a path to an image file."""
    if not os.path.exists(text):
        return False
    from pathlib import Path
    return Path(text).suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")


def _is_youtube(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url


def _is_github(url: str) -> bool:
    return "github.com" in url


def _is_pdf(path: str) -> bool:
    return path.endswith(".pdf") or "/pdf/" in path


def _print_banner():
    console.print(BANNER)


def _print_status():
    """Print current status line."""
    try:
        summary = scheduler.get_study_summary()
        parts = []
        if summary["due_now"] > 0:
            parts.append(f"[cyan]{summary['due_now']} due[/cyan]")
        if summary["total_concepts"] > 0:
            parts.append(f"[dim]{summary['total_concepts']} concepts[/dim]")
        if summary["mastered"] > 0:
            parts.append(f"[green]{summary['mastered']} mastered[/green]")
        if parts:
            console.print(" • ".join(parts))
    except:
        pass


def _check_api_keys():
    """Check for required API keys."""
    if not os.environ.get("GROQ_API_KEY"):
        console.print("[red]Error: GROQ_API_KEY not set[/red]")
        console.print()
        console.print("[dim]Get your free API key:[/dim]")
        console.print("  1. Go to [cyan]https://console.groq.com[/cyan]")
        console.print("  2. Create account and get API key")
        console.print("  3. Run: [white]export GROQ_API_KEY=your_key[/white]")
        console.print()
        console.print("[dim]Or add to ~/.bashrc for persistence[/dim]")
        return False
    return True


# ============ COMMANDS ============

def cmd_add(url: str) -> bool:
    """Add content from URL."""
    url = url.strip()
    if not url:
        console.print("[yellow]Usage: /add <url>[/yellow]")
        return True
    
    # Check if exists
    existing = storage.get_source_by_url(url)
    if existing:
        console.print(f"[yellow]Already added:[/yellow] {existing['title']}")
        concepts = storage.get_concepts_for_source(existing["id"])
        console.print(f"[dim]{len(concepts)} concepts[/dim]")
        return True
    
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    
    with Progress(
        SpinnerColumn(style="cyan"),
        BarColumn(bar_width=20, complete_style="cyan", finished_style="green"),
        TextColumn("[bold]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Fetching content...", total=4)
        
        # Step 1: Fetch based on URL type
        if _is_youtube(url):
            result = extract_youtube(url)
        elif _is_github(url):
            result = extract_github(url)
        elif _is_pdf(url):
            result = extract_pdf(url)
        else:
            result = extract_article(url)
        
        if "error" in result:
            progress.stop()
            console.print(f"[red]Error: {result['error']}[/red]")
            return True
        
        progress.update(task, advance=1, description="Generating title...")
        
        # Step 2: Title
        title = llm.generate_title(result["content"], result["title"])
        progress.update(task, advance=1, description="Extracting concepts...")
        
        # Step 3: Concepts
        try:
            concepts = llm.extract_concepts(result["content"], title)
        except Exception as e:
            progress.stop()
            console.print(f"[red]Error: Failed to extract concepts: {e}[/red]")
            return True
        
        if not concepts:
            progress.stop()
            console.print("[red]Error: No concepts found[/red]")
            return True
        
        progress.update(task, advance=1, description="Saving...")
        
        # Step 4: Store
        source_id = storage.add_source(
            url=result["url"],
            title=title,
            source_type=result["source_type"],
            raw_content=result["content"]
        )
        
        for c in concepts:
            storage.add_concept(source_id, c["name"], c["source_quote"], c.get("question"))
        
        progress.update(task, advance=1, description="Done!")
    
    console.print(f"[green]OK[/green] {title}")
    console.print(f"[green]OK[/green] Added {len(concepts)} concepts:")
    for c in concepts:
        console.print(f"  [dim]•[/dim] {c['name']}")
    
    console.print()
    console.print(f"[cyan]{len(concepts)} concepts ready to study![/cyan]")
    console.print("[dim]Run /study to start, or press Enter[/dim]")
    
    return True


def cmd_study() -> bool:
    """Interactive study session with Socratic adversarial coaching."""
    from .coach import create_coach
    
    due = scheduler.get_next_due()
    
    if not due:
        summary = scheduler.get_study_summary()
        if summary["total_concepts"] == 0:
            console.print("[dim]No concepts yet. Add some content first:[/dim]")
            console.print("  [cyan]/add[/cyan] <youtube-url>")
        else:
            console.print("[green]OK[/green] All caught up! Nothing due for review.")
        return True
    
    total_due = len(scheduler.get_all_due())
    studied = 0
    
    console.print()
    console.print(f"[bold cyan]Study Session[/bold cyan] — {total_due} concepts to review")
    console.print("[dim]Type 'skip' to skip, 'q' to quit anytime[/dim]")
    console.print("[dim]⚔️  Adversarial mode: I'll challenge your understanding[/dim]")
    
    while due:
        studied += 1
        
        # Create Socratic coach for this concept
        coach = create_coach(
            concept_name=due["name"],
            source_quote=due["source_quote"],
            question=due.get("question")
        )
        
        # Concept header
        console.print()
        console.print(f"[bold]━━━ {studied}/{total_due}: {due['name']} ━━━[/bold]")
        console.print(f"[dim]from {due['source_title']}[/dim]")
        
        # Challenge question
        console.print()
        console.print(f"[cyan]Challenge:[/cyan] {coach.get_initial_challenge()}")
        
        # Source hint
        console.print()
        hint_text = due['source_quote'][:100] + "..." if len(due['source_quote']) > 100 else due['source_quote']
        console.print(f"[dim]Hint: \"{hint_text}\"[/dim]")
        
        # Multi-turn dialogue loop
        all_explanations = []
        
        while not coach.finished:
            console.print()
            console.print("[dim](Press Enter twice when done)[/dim]")
            
            _flush_stdin()
            lines = []
            try:
                while True:
                    line = console.input("[bold]> [/bold]" if not lines else "[bold]  [/bold]")
                    if not line and lines:
                        break
                    if line:
                        lines.append(line)
                    elif not lines:
                        console.print("[yellow]Say something, or type 'skip' to skip.[/yellow]")
            except (EOFError, KeyboardInterrupt):
                console.print("\n[dim]Session ended.[/dim]")
                return True
            
            _flush_stdin()
            explanation = " ".join(lines).strip()
            
            # Handle commands
            if explanation.lower() in ("q", "quit", "/quit", "exit"):
                console.print("[dim]Session ended.[/dim]")
                return True
            
            if explanation.lower() in ("skip", "s", "/skip"):
                storage.skip_concept(due["id"])
                console.print("[yellow]⏭ Skipped — won't appear again[/yellow]")
                break
            
            if not explanation:
                console.print("[yellow]Say something, or type 'skip' to skip.[/yellow]")
                continue
            
            # Check if user provided an image path - extract text via OCR
            if _is_image_path(explanation):
                with _spinner("Extracting text from image..."):
                    from .ocr import extract_text_from_image, check_relevance
                    ocr_result = extract_text_from_image(explanation)
                
                if "error" in ocr_result:
                    console.print(f"[red]Error: {ocr_result['error']}[/red]")
                    continue
                
                if not ocr_result["text"].strip():
                    console.print("[yellow]No text found in image. Try again.[/yellow]")
                    continue
                
                extracted_text = ocr_result["text"]
                
                # Check if extracted text is relevant to the concept
                with _spinner("Checking relevance..."):
                    relevance = check_relevance(extracted_text, due["name"], due["source_quote"])
                
                if not relevance["is_relevant"]:
                    console.print(f"[red]Error: Image content not related to '{due['name']}'[/red]")
                    console.print(f"[dim]Detected: \"{extracted_text[:80]}...\"[/dim]")
                    console.print("[yellow]Please provide an explanation related to the topic.[/yellow]")
                    continue
                
                explanation = extracted_text
                console.print(f"[dim]📷 Extracted: \"{explanation[:100]}{'...' if len(explanation) > 100 else ''}\"[/dim]")
            
            all_explanations.append(explanation)
            
            # Get coach response
            with _spinner("Analyzing..."):
                result = coach.respond(explanation)
            
            console.print()
            
            if result["type"] == "followup":
                # Show follow-up challenge
                console.print(f"[yellow]{result['message']}[/yellow]")
            else:
                # Final result
                _show_coach_result(result)
                
                # Store
                storage.add_explanation(
                    concept_id=due["id"],
                    text=" | ".join(all_explanations),
                    score=result["score"],
                    covered=", ".join(result["strengths"]) if result["strengths"] else None,
                    missed=", ".join(result["holes"][:3]) if result["holes"] else None,
                    feedback=result["message"]
                )
                
                # Update scheduler
                sched_result = scheduler.update_after_review(due["id"], result["score"])
                console.print()
                console.print(f"[dim]Next review: Next review: {sched_result['next_review']}[/dim]")
        
        # Check if skipped (break from inner loop)
        if explanation.lower() in ("skip", "s", "/skip"):
            due = scheduler.get_next_due()
            total_due = len(scheduler.get_all_due()) + studied
            continue
        
        # Get next concept
        due = scheduler.get_next_due()
        
        if due:
            remaining = len(scheduler.get_all_due())
            console.print()
            try:
                cont = console.input(f"[dim]({remaining} more) Press Enter to continue, 'q' to quit: [/dim]").strip()
                if cont.lower() in ("q", "quit", "n", "no"):
                    console.print("[dim]Session ended.[/dim]")
                    return True
            except (EOFError, KeyboardInterrupt):
                console.print("\n[dim]Session ended.[/dim]")
                return True
    
    console.print()
    console.print(f"[green]OK[/green] Done! Reviewed {studied} concepts.")
    return True


def _show_coach_result(result: dict):
    """Display Socratic coach final result."""
    score = result["score"]
    
    # Visual score bar
    stars = "█" * score + "░" * (5 - score)
    labels = {1: "Needs Work", 2: "Getting There", 3: "Good", 4: "Great", 5: "Perfect"}
    label = labels.get(score, "")
    
    if score >= 4:
        console.print(f"[green]{stars}[/green] [bold green]{label}[/bold green]")
    elif score >= 3:
        console.print(f"[yellow]{stars}[/yellow] [bold yellow]{label}[/bold yellow]")
    else:
        console.print(f"[red]{stars}[/red] [bold red]{label}[/bold red]")
    
    # Feedback
    if result.get("message"):
        console.print(f"[dim]{result['message']}[/dim]")
    
    # Strengths
    if result.get("strengths"):
        console.print("[green]Solid understanding:[/green]")
        for s in result["strengths"][:2]:
            # Truncate long strengths
            s_short = s[:150] + "..." if len(s) > 150 else s
            console.print(f"  [green]•[/green] {s_short}")
    
    # Holes found
    if result.get("holes"):
        console.print("[red]Gaps exposed:[/red]")
        for h in result["holes"][:3]:
            # Truncate long holes
            h_short = h[:150] + "..." if len(h) > 150 else h
            console.print(f"  [red]•[/red] {h_short}")


def _show_evaluation_result(result: dict):
    """Display evaluation result with visual score bar."""
    score = result["score"]
    
    # Visual score bar (█ filled, ░ empty)
    stars = "█" * score + "░" * (5 - score)
    
    # Score display with color and label
    labels = {1: "Needs Work", 2: "Getting There", 3: "Good", 4: "Great", 5: "Perfect"}
    label = labels.get(score, "")
    
    if score >= 4:
        console.print(f"[green]{stars}[/green] [bold green]{label}[/bold green]")
    elif score >= 3:
        console.print(f"[yellow]{stars}[/yellow] [bold yellow]{label}[/bold yellow]")
    else:
        console.print(f"[red]{stars}[/red] [bold red]{label}[/bold red]")
    
    # Feedback
    if result["feedback"]:
        console.print(f"[dim]{result['feedback']}[/dim]")
    
    # Covered/Missed as bullet points
    if result["covered"]:
        console.print("[green]You got:[/green]")
        for item in result["covered"][:3]:
            console.print(f"  [green]•[/green] {item}")
    
    if result["missed"]:
        console.print("[red]You missed:[/red]")
        for item in result["missed"][:3]:
            console.print(f"  [red]•[/red] {item}")


def cmd_stats() -> bool:
    """Show statistics."""
    stats = storage.get_stats()
    summary = scheduler.get_study_summary()
    
    if stats["total_sources"] == 0:
        console.print("[dim]No data yet. Start by adding content:[/dim]")
        console.print("  [cyan]/add[/cyan] <url>")
        return True
    
    table = Table(box=box.ROUNDED, show_header=False, border_style="cyan")
    table.add_column("", style="dim", width=15)
    table.add_column("", style="bold")
    
    table.add_row("Sources", str(stats["total_sources"]))
    table.add_row("Concepts", str(stats["total_concepts"]))
    table.add_row("Due now", f"[cyan]{summary['due_now']}[/cyan]" if summary["due_now"] > 0 else "[dim]0[/dim]")
    table.add_row("Reviews", str(stats["total_reviews"]))
    
    if stats["avg_score"] > 0:
        score_color = "green" if stats["avg_score"] >= 4 else "yellow" if stats["avg_score"] >= 3 else "red"
        table.add_row("Avg score", f"[{score_color}]{stats['avg_score']}/5[/{score_color}]")
    
    table.add_row("Mastered", f"[green]{summary['mastered']}[/green]" if summary["mastered"] > 0 else "[dim]0[/dim]")
    
    if stats["skipped_concepts"] > 0:
        table.add_row("Skipped", f"[dim]{stats['skipped_concepts']}[/dim]")
    
    console.print(Panel(table, title="[bold]Your Progress[/bold]", border_style="cyan"))
    return True


def cmd_list(args: str = "") -> bool:
    """List sources and concepts."""
    if args.strip() in ("-s", "--sources", "sources"):
        sources = storage.get_all_sources()
        if not sources:
            console.print("[dim]No sources yet.[/dim]")
            return True
        
        for s in sources:
            concepts = storage.get_concepts_for_source(s["id"])
            console.print(f"[bold]{s['title']}[/bold] [dim]({len(concepts)} concepts)[/dim]")
            console.print(f"  [dim]{s['url']}[/dim]")
        return True
    
    concepts = storage.get_all_concepts()
    if not concepts:
        console.print("[dim]No concepts yet. Add some content:[/dim]")
        console.print("  [cyan]/add[/cyan] <url>")
        return True
    
    # Group by source
    by_source = {}
    for c in concepts:
        src = c["source_title"]
        if src not in by_source:
            by_source[src] = []
        by_source[src].append(c)
    
    for src_title, src_concepts in by_source.items():
        console.print(f"\n[bold]{src_title}[/bold]")
        for c in src_concepts:
            progress = storage.get_progress(c["id"])
            if progress and progress["review_count"] > 0:
                score = progress.get("last_score")
                score_str = f"[dim]({progress['review_count']}x"
                if score:
                    score_str += f", last: {score}/5"
                score_str += ")[/dim]"
                console.print(f"  • {c['name']} {score_str}")
            else:
                console.print(f"  • {c['name']} [dim](new)[/dim]")
    
    return True


def cmd_due() -> bool:
    """Show due concepts."""
    due = scheduler.get_all_due()
    
    if not due:
        console.print("[green]OK[/green] Nothing due! All caught up.")
        return True
    
    console.print(f"[bold]{len(due)} concepts due for review:[/bold]")
    console.print()
    
    for d in due:
        console.print(f"  • {d['name']}")
        console.print(f"    [dim]{d['source_title']}[/dim]")
    
    console.print()
    console.print("[dim]Run /study to start reviewing[/dim]")
    return True


def cmd_skip(name: str) -> bool:
    """Skip a concept."""
    name = name.strip()
    if not name:
        console.print("[yellow]Usage: /skip <concept-name>[/yellow]")
        return True
    
    concepts = storage.get_all_concepts()
    matches = [c for c in concepts if name.lower() in c["name"].lower()]
    
    if not matches:
        console.print(f"[red]No concept matching '{name}'[/red]")
        return True
    
    if len(matches) > 1:
        console.print("[yellow]Multiple matches:[/yellow]")
        for m in matches:
            console.print(f"  • {m['name']}")
        console.print("[dim]Be more specific.[/dim]")
        return True
    
    storage.skip_concept(matches[0]["id"])
    console.print(f"[green]OK[/green] Skipped: {matches[0]['name']}")
    return True


def cmd_unskip(name: str) -> bool:
    """Unskip a concept."""
    name = name.strip()
    if not name:
        # Show all skipped
        with storage.get_db() as conn:
            rows = conn.execute("""
                SELECT c.*, s.title as source_title
                FROM concepts c JOIN sources s ON c.source_id = s.id
                WHERE c.skipped = 1
            """).fetchall()
            skipped = [dict(r) for r in rows]
        
        if not skipped:
            console.print("[dim]No skipped concepts.[/dim]")
            return True
        
        console.print("[bold]Skipped concepts:[/bold]")
        for s in skipped:
            console.print(f"  • {s['name']}")
        console.print()
        console.print("[dim]Usage: /unskip <name>[/dim]")
        return True
    
    with storage.get_db() as conn:
        rows = conn.execute("""
            SELECT c.*, s.title as source_title
            FROM concepts c JOIN sources s ON c.source_id = s.id
            WHERE c.skipped = 1
        """).fetchall()
        skipped = [dict(r) for r in rows]
    
    matches = [c for c in skipped if name.lower() in c["name"].lower()]
    
    if not matches:
        console.print(f"[red]No skipped concept matching '{name}'[/red]")
        return True
    
    if len(matches) > 1:
        console.print("[yellow]Multiple matches:[/yellow]")
        for m in matches:
            console.print(f"  • {m['name']}")
        return True
    
    storage.unskip_concept(matches[0]["id"])
    console.print(f"[green]OK[/green] Restored: {matches[0]['name']}")
    return True


def cmd_config() -> bool:
    """Show configuration."""
    console.print("[bold]Configuration:[/bold]")
    console.print()
    console.print(f"  Data directory: [cyan]{config.DATA_DIR}[/cyan]")
    console.print(f"  Database: [cyan]{config.DB_PATH}[/cyan]")
    console.print()
    console.print(f"  Groq model: [dim]{config.GROQ_MODEL}[/dim]")
    console.print(f"  Gemini model: [dim]{config.GEMINI_MODEL}[/dim]")
    console.print()
    console.print(f"  GROQ_API_KEY: [green]set[/green]" if os.environ.get("GROQ_API_KEY") else "  GROQ_API_KEY: [red]not set[/red]")
    console.print(f"  GEMINI_API_KEY: [green]set[/green]" if os.environ.get("GEMINI_API_KEY") else "  GEMINI_API_KEY: [dim]not set (optional)[/dim]")
    return True


def cmd_help() -> bool:
    """Show help."""
    console.print(HELP_TEXT)
    return True


def cmd_clear() -> bool:
    """Clear screen."""
    console.clear()
    _print_banner()
    return True


# ============ COMMAND ROUTER ============

COMMANDS: dict[str, Callable] = {
    "add": lambda args: cmd_add(args),
    "study": lambda args: cmd_study(),
    "stats": lambda args: cmd_stats(),
    "list": lambda args: cmd_list(args),
    "ls": lambda args: cmd_list(args),
    "due": lambda args: cmd_due(),
    "skip": lambda args: cmd_skip(args),
    "unskip": lambda args: cmd_unskip(args),
    "config": lambda args: cmd_config(),
    "help": lambda args: cmd_help(),
    "h": lambda args: cmd_help(),
    "?": lambda args: cmd_help(),
    "clear": lambda args: cmd_clear(),
    "cls": lambda args: cmd_clear(),
    "quit": lambda args: False,
    "exit": lambda args: False,
    "q": lambda args: False,
}


def handle_input(user_input: str) -> bool:
    """Handle user input. Returns False to exit."""
    user_input = user_input.strip()
    
    if not user_input:
        # Empty input = start study
        return cmd_study()
    
    # Slash command
    if user_input.startswith("/"):
        parts = user_input[1:].split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd in COMMANDS:
            result = COMMANDS[cmd](args)
            return result if result is not None else True
        else:
            console.print(f"[red]Unknown command: /{cmd}[/red]")
            console.print("[dim]Type /help for available commands[/dim]")
            return True
    
    # URL or local file detection
    if _is_url(user_input) or _is_local_file(user_input):
        return cmd_add(user_input)
    
    # Unknown input
    console.print(f"[dim]Unknown input. Type /help for commands.[/dim]")
    return True


# ============ MAIN LOOP ============

def interactive_mode():
    """Run interactive REPL."""
    console.clear()
    _print_banner()
    console.print()
    _print_status()
    console.print()
    console.print("[dim]Type /help for commands, or paste a URL to add content[/dim]")
    console.print("[dim]Press Enter to start studying[/dim]")
    console.print()
    
    while True:
        try:
            user_input = Prompt.ask("[bold cyan]learnlock[/bold cyan]", console=console)
            console.print()
            
            if not handle_input(user_input):
                console.print("[dim]Goodbye![/dim]")
                break
                
            console.print()
        except (EOFError, KeyboardInterrupt):
            console.print()
            console.print("[dim]Goodbye![/dim]")
            break


# ============ CLI ENTRY POINTS ============

@app.command()
def cli(
    prompt: Optional[str] = typer.Argument(None, help="Command or URL to process"),
    print_mode: bool = typer.Option(False, "-p", "--print", help="Print output and exit (non-interactive)"),
    version: bool = typer.Option(False, "-v", "--version", help="Show version"),
):
    """
    learn-lock - Stop consuming. Start retaining.
    
    Run without arguments for interactive mode.
    """
    if version:
        console.print(f"learnlock {VERSION}")
        return
    
    # Ensure data directory
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check API keys
    if not _check_api_keys():
        raise typer.Exit(1)
    
    if print_mode and prompt:
        # Non-interactive mode
        handle_input(prompt)
    elif prompt:
        # Single command then interactive
        console.clear()
        _print_banner()
        console.print()
        handle_input(prompt)
        console.print()
        interactive_mode()
    else:
        # Interactive mode
        interactive_mode()


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
