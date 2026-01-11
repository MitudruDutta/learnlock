"""learn-lock CLI - Interactive learning system like Claude Code."""

import sys
import os
import json
import re
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
from .tools import extract_youtube, extract_article

# ============ CONSTANTS ============
VERSION = "0.1.0"
BANNER = """[bold cyan]
 ╦  ╔═╗╔═╗╦═╗╔╗╔╦  ╔═╗╔═╗╦╔═
 ║  ║╣ ╠═╣╠╦╝║║║║  ║ ║║  ╠╩╗
 ╩═╝╚═╝╩ ╩╩╚═╝╚╝╩═╝╚═╝╚═╝╩ ╩[/bold cyan]
[dim]Stop consuming. Start retaining.[/dim]
"""

HELP_TEXT = """
[bold]Commands:[/bold]
  [cyan]/add[/cyan] <url>        Add YouTube or article
  [cyan]/study[/cyan]            Study due concepts
  [cyan]/stats[/cyan]            Show your progress
  [cyan]/list[/cyan]             List all concepts
  [cyan]/due[/cyan]              Show what's due
  [cyan]/skip[/cyan] <name>      Skip a concept
  [cyan]/unskip[/cyan] <name>    Restore skipped concept
  [cyan]/config[/cyan]           Show configuration
  [cyan]/clear[/cyan]            Clear screen
  [cyan]/help[/cyan]             Show this help
  [cyan]/quit[/cyan]             Exit

[bold]Tips:[/bold]
  • Just type a URL to add it
  • Press Enter with no input to start studying
  • Type 'skip' during study to skip current concept
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


def _is_youtube(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url


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
        console.print("[red]✗ GROQ_API_KEY not set[/red]")
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
        return False
    
    # Check if exists
    existing = storage.get_source_by_url(url)
    if existing:
        console.print(f"[yellow]Already added:[/yellow] {existing['title']}")
        concepts = storage.get_concepts_for_source(existing["id"])
        console.print(f"[dim]{len(concepts)} concepts[/dim]")
        return True
    
    # Extract content
    with _spinner("Fetching content..."):
        if _is_youtube(url):
            result = extract_youtube(url)
        else:
            result = extract_article(url)
    
    if "error" in result:
        console.print(f"[red]✗ {result['error']}[/red]")
        return False
    
    console.print(f"[green]✓[/green] {result['title']}")
    
    # Extract concepts
    with _spinner("Extracting concepts..."):
        try:
            concepts = llm.extract_concepts(result["content"], result["title"])
        except Exception as e:
            console.print(f"[red]✗ Failed to extract concepts: {e}[/red]")
            return False
    
    if not concepts:
        console.print("[red]✗ No concepts found[/red]")
        return False
    
    # Store
    source_id = storage.add_source(
        url=result["url"],
        title=result["title"],
        source_type=result["source_type"],
        raw_content=result["content"]
    )
    
    for c in concepts:
        storage.add_concept(source_id, c["name"], c["source_quote"])
    
    console.print(f"[green]✓[/green] Added {len(concepts)} concepts:")
    for c in concepts:
        console.print(f"  [dim]•[/dim] {c['name']}")
    
    return True


def cmd_study() -> bool:
    """Interactive study session."""
    due = scheduler.get_next_due()
    
    if not due:
        summary = scheduler.get_study_summary()
        if summary["total_concepts"] == 0:
            console.print("[dim]No concepts yet. Add some content first:[/dim]")
            console.print("  [cyan]/add[/cyan] <youtube-url>")
            console.print("  [cyan]/add[/cyan] <article-url>")
        else:
            console.print("[green]✓[/green] All caught up! Nothing due for review.")
        return True
    
    total_due = len(scheduler.get_all_due())
    studied = 0
    
    while due:
        studied += 1
        console.clear()
        _print_banner()
        
        # Progress indicator
        console.print(f"[dim]Concept {studied} of {total_due}[/dim]")
        console.print()
        
        # Concept panel
        console.print(Panel(
            f"[bold white]{due['name']}[/bold white]",
            subtitle=f"[dim]{due['source_title']}[/dim]",
            border_style="cyan",
            padding=(0, 2),
        ))
        
        # Source quote
        console.print()
        console.print("[bold]📖 Source says:[/bold]")
        console.print(Panel(
            due["source_quote"],
            border_style="dim",
            padding=(1, 2),
        ))
        
        # Prompt for explanation
        console.print()
        console.print("[bold]✏️  Explain in your own words:[/bold]")
        console.print("[dim]   (type 'skip' to skip, 'quit' to exit)[/dim]")
        console.print()
        
        try:
            explanation = Prompt.ask("[cyan]>[/cyan]", console=console)
        except (EOFError, KeyboardInterrupt):
            console.print()
            return True
        
        explanation = explanation.strip()
        
        if explanation.lower() in ("quit", "q", "/quit"):
            return True
        
        if explanation.lower() in ("skip", "s", "/skip"):
            storage.skip_concept(due["id"])
            console.print("[yellow]⏭ Skipped[/yellow]")
            due = scheduler.get_next_due()
            total_due = len(scheduler.get_all_due()) + studied
            if due:
                Prompt.ask("[dim]Press Enter to continue[/dim]", console=console)
            continue
        
        if not explanation:
            console.print("[yellow]Empty response. Type something or 'skip'.[/yellow]")
            Prompt.ask("[dim]Press Enter[/dim]", console=console)
            continue
        
        # Evaluate
        with _spinner("Evaluating your explanation..."):
            eval_result = llm.evaluate_explanation(
                concept_name=due["name"],
                source_quote=due["source_quote"],
                user_explanation=explanation
            )
        
        # Show results
        console.print()
        _show_evaluation_result(eval_result)
        
        # Store
        storage.add_explanation(
            concept_id=due["id"],
            text=explanation,
            score=eval_result["score"],
            covered=", ".join(eval_result["covered"]) if eval_result["covered"] else None,
            missed=", ".join(eval_result["missed"]) if eval_result["missed"] else None,
            feedback=eval_result["feedback"]
        )
        
        # Update scheduler
        sched_result = scheduler.update_after_review(due["id"], eval_result["score"])
        
        console.print()
        console.print(f"[dim]Next review: {sched_result['next_review']}[/dim]")
        
        # Next?
        due = scheduler.get_next_due()
        if due:
            console.print()
            try:
                cont = Prompt.ask(
                    f"[dim]{len(scheduler.get_all_due())} more due. Continue? (Enter/q)[/dim]",
                    console=console,
                    default=""
                )
                if cont.lower() in ("q", "quit", "n", "no"):
                    return True
            except (EOFError, KeyboardInterrupt):
                return True
    
    console.print()
    console.print("[green]✓[/green] Study session complete!")
    return True


def _show_evaluation_result(result: dict):
    """Display evaluation result."""
    score = result["score"]
    
    # Score display
    if score >= 4:
        score_color = "green"
        emoji = "🎯"
        msg = "Excellent!"
    elif score >= 3:
        score_color = "yellow"
        emoji = "📝"
        msg = "Good, but review the gaps"
    else:
        score_color = "red"
        emoji = "📚"
        msg = "Needs more review"
    
    # Score panel
    score_text = f"{emoji} [bold {score_color}]{score}/5[/bold {score_color}] {msg}"
    console.print(Panel(score_text, border_style=score_color))
    
    # Feedback
    if result["feedback"]:
        console.print()
        console.print(f"[italic]{result['feedback']}[/italic]")
    
    # Covered/Missed
    if result["covered"]:
        console.print()
        console.print("[green]✓ You covered:[/green]")
        for p in result["covered"]:
            console.print(f"  • {p}")
    
    if result["missed"]:
        console.print()
        console.print("[red]✗ You missed:[/red]")
        for p in result["missed"]:
            console.print(f"  • {p}")


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
        console.print("[green]✓[/green] Nothing due! All caught up.")
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
        return False
    
    concepts = storage.get_all_concepts()
    matches = [c for c in concepts if name.lower() in c["name"].lower()]
    
    if not matches:
        console.print(f"[red]No concept matching '{name}'[/red]")
        return False
    
    if len(matches) > 1:
        console.print("[yellow]Multiple matches:[/yellow]")
        for m in matches:
            console.print(f"  • {m['name']}")
        console.print("[dim]Be more specific.[/dim]")
        return False
    
    storage.skip_concept(matches[0]["id"])
    console.print(f"[green]✓[/green] Skipped: {matches[0]['name']}")
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
        return False
    
    if len(matches) > 1:
        console.print("[yellow]Multiple matches:[/yellow]")
        for m in matches:
            console.print(f"  • {m['name']}")
        return False
    
    storage.unskip_concept(matches[0]["id"])
    console.print(f"[green]✓[/green] Restored: {matches[0]['name']}")
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
    
    # URL detection
    if _is_url(user_input):
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
