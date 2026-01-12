"use client";

import { useEffect, useState, useRef } from "react";

const ASCII_LOGO = `██╗     ███████╗ █████╗ ██████╗ ███╗   ██╗██╗      ██████╗  ██████╗██╗  ██╗
██║     ██╔════╝██╔══██╗██╔══██╗████╗  ██║██║     ██╔═══██╗██╔════╝██║ ██╔╝
██║     █████╗  ███████║██████╔╝██╔██╗ ██║██║     ██║   ██║██║     █████╔╝ 
██║     ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║██║     ██║   ██║██║     ██╔═██╗ 
███████╗███████╗██║  ██║██║  ██║██║ ╚████║███████╗╚██████╔╝╚██████╗██║  ██╗
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝`;

const MOBILE_LOGO = `LEARNLOCK`;

const STEPS = [
  { text: "learnlock", type: "command", delay: 800 },
  { 
    text: `[ascii]The app that argues with you.`, 
    type: "output", 
    delay: 200 
  },
  { text: "/add https://youtu.be/kCc8FmEb1nY", type: "input", delay: 1000 },
  { 
    text: `[cyan]•[/cyan] Fetching transcript...
[cyan]•[/cyan] Extracting concepts...
[cyan]•[/cyan] Generating claims...
[green]OK[/green] Added: GPT from Scratch - Andrej Karpathy
[green]OK[/green] 8 concepts with 24 falsifiable claims`, 
    type: "output", 
    delay: 800 
  },
  { text: "/study", type: "input", delay: 1000 },
  { 
    text: `
[bold cyan]═══ DUEL ENGINE ═══[/bold cyan]

[bold]Concept:[/bold] Self-Attention Mechanism
[dim]from GPT from Scratch[/dim]

[cyan]┌─ CLAIMS (3) ─────────────────────────────┐[/cyan]
[dim]│[/dim] Computes weighted sum of value vectors
[dim]│[/dim] Weights derived from query-key dot product
[dim]│[/dim] Scaled by √d_k to prevent gradient issues
[cyan]└──────────────────────────────────────────┘[/cyan]

[yellow]Challenge:[/yellow] Explain how self-attention computes its output.`,
    type: "output", 
    delay: 800 
  },
  { text: "It looks at all the words and picks the important ones.", type: "input", delay: 1500 },
  { 
    text: `[cyan]┌─ BELIEF MODEL ───────────────────────────┐[/cyan]
[dim]│[/dim] [yellow]⚠[/yellow] Vague: "picks important ones"
[dim]│[/dim] [red]✗[/red] Missing: weighted sum mechanism
[dim]│[/dim] [red]✗[/red] Missing: query-key computation
[cyan]└──────────────────────────────────────────┘[/cyan]

[yellow]Turn 1/3[/yellow] — You said it "picks" words. [bold]HOW[/bold] does it decide which are important? What mathematical operation produces the weights?`, 
    type: "output", 
    delay: 500 
  },
  { text: "It uses dot product between queries and keys to get attention scores.", type: "input", delay: 1500 },
  { 
    text: `[cyan]┌─ BELIEF MODEL ───────────────────────────┐[/cyan]
[dim]│[/dim] [green]✓[/green] Query-key dot product
[dim]│[/dim] [red]✗[/red] Missing: weighted sum of values
[dim]│[/dim] [red]✗[/red] Missing: scaling factor
[cyan]└──────────────────────────────────────────┘[/cyan]

[yellow]Turn 2/3[/yellow] — Good. Now what happens AFTER you have the attention scores?`, 
    type: "output", 
    delay: 500 
  },
  { text: "Softmax the scores, then multiply with value vectors to get weighted sum.", type: "input", delay: 1500 },
  { 
    text: `[cyan]┌─ BELIEF MODEL ───────────────────────────┐[/cyan]
[dim]│[/dim] [green]✓[/green] Query-key dot product
[dim]│[/dim] [green]✓[/green] Weighted sum of values
[dim]│[/dim] [yellow]⚠[/yellow] Partial: scaling not mentioned
[cyan]└──────────────────────────────────────────┘[/cyan]

[green]═══ REVEAL ═══[/green]

[bold]Belief Trajectory:[/bold]
  Turn 1: [red]▁[/red] vague, no mechanism
  Turn 2: [yellow]▃[/yellow] partial, got Q·K
  Turn 3: [green]▆[/green] solid, missing scale

[bold]Claims Satisfied:[/bold] 2/3
[bold]Score:[/bold] [green]||||[/green][dim].[/dim] 4/5 — Great

[dim]Scaling by √d_k prevents softmax saturation. Review in 4 days.[/dim]`, 
    type: "output", 
    delay: 500 
  },
  { text: "/stats", type: "input", delay: 1000 },
  { 
    text: `[cyan]╭────────────────────────────╮[/cyan]
[cyan]│[/cyan]      [bold]Your Progress[/bold]         [cyan]│[/cyan]
[cyan]├────────────────────────────┤[/cyan]
[cyan]│[/cyan] Sources         [bold]1[/bold]          [cyan]│[/cyan]
[cyan]│[/cyan] Concepts        [bold]8[/bold]          [cyan]│[/cyan]
[cyan]│[/cyan] Due now         [bold]7[/bold]          [cyan]│[/cyan]
[cyan]│[/cyan] Avg score       [bold]4.0/5[/bold]      [cyan]│[/cyan]
[cyan]│[/cyan] Mastered        [bold]1[/bold]          [cyan]│[/cyan]
[cyan]╰────────────────────────────╯[/cyan]`, 
    type: "output", 
    delay: 500 
  }
];

export function TerminalDemo() {
  const [lines, setLines] = useState<{ content: string; type: string }[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [typingText, setTypingText] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {


    const processStep = async () => {
      if (currentStep >= STEPS.length) return;

      const step = STEPS[currentStep];

      if (step.type === "command" || step.type === "input") {
        for (let i = 0; i <= step.text.length; i++) {
          setTypingText(step.text.slice(0, i));
          await new Promise(r => setTimeout(r, 20 + Math.random() * 20));
        }
        await new Promise(r => setTimeout(r, 300));
        setLines(prev => [...prev, { content: step.text, type: step.type }]);
        setTypingText("");
        setCurrentStep(c => c + 1);
      } else {
        await new Promise(r => setTimeout(r, step.delay));
        setLines(prev => [...prev, { content: step.text, type: "output" }]);
        setCurrentStep(c => c + 1);
      }
    };

    const timeout = setTimeout(processStep, 100);
    return () => clearTimeout(timeout);
  }, [currentStep]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [lines, typingText]);

  return (
    <div className="w-full h-full flex flex-col overflow-hidden rounded-md sm:rounded-lg border border-border bg-[#18181b] shadow-2xl">
      <div className="flex items-center gap-1.5 sm:gap-2 px-2 sm:px-4 py-2 sm:py-3 border-b border-white/10 bg-[#27272a] shrink-0">
        <div className="flex gap-1 sm:gap-2">
          <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-full bg-red-500" />
          <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-full bg-yellow-500" />
          <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-full bg-green-500" />
        </div>
        <div className="flex-1 text-center text-[10px] sm:text-xs text-white/40 font-mono">learnlock — zsh</div>
      </div>
      
      <div 
        ref={scrollRef}
        className="p-2 sm:p-4 flex-1 overflow-y-auto overflow-x-hidden font-mono text-[10px] sm:text-xs md:text-sm leading-relaxed scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent text-white/90"
      >
        {lines.map((line, i) => (
          <div key={i} className="mb-1 whitespace-pre-wrap wrap-break-word">
            {line.type === "command" && <span className="text-green-500 mr-1 sm:mr-2">➜ ~</span>}
            {line.type === "input" && <span className="text-cyan-500 mr-1 sm:mr-2 font-bold">ll&gt;</span>}
            <span 
              className={line.type === "command" || line.type === "input" ? "text-white" : "text-white/80"}
              dangerouslySetInnerHTML={{ 
                __html: line.content
                  .replace(/\[ascii\]/g, typeof window !== 'undefined' && window.innerWidth < 640 ? `<span class="text-cyan-400 font-bold text-lg">${MOBILE_LOGO}</span>\n` : `<span class="hidden sm:inline whitespace-pre">${ASCII_LOGO}</span><span class="sm:hidden text-cyan-400 font-bold text-base">LEARNLOCK</span>\n`)
                  .replace(/\[cyan\](.*?)\[\/cyan\]/g, '<span class="text-cyan-400">$1</span>')
                  .replace(/\[green\](.*?)\[\/green\]/g, '<span class="text-green-400">$1</span>')
                  .replace(/\[yellow\](.*?)\[\/yellow\]/g, '<span class="text-yellow-400">$1</span>')
                  .replace(/\[red\](.*?)\[\/red\]/g, '<span class="text-red-400">$1</span>')
                  .replace(/\[bold\](.*?)\[\/bold\]/g, '<span class="font-bold text-white">$1</span>')
                  .replace(/\[bold cyan\](.*?)\[\/bold cyan\]/g, '<span class="font-bold text-cyan-400">$1</span>')
                  .replace(/\[dim\](.*?)\[\/dim\]/g, '<span class="text-white/40">$1</span>')
              }}
            />
          </div>
        ))}
        {currentStep < STEPS.length && (STEPS[currentStep].type === "command" || STEPS[currentStep].type === "input") && (
          <div className="mb-1">
            {STEPS[currentStep].type === "command" && <span className="text-green-500 mr-1 sm:mr-2">➜ ~</span>}
            {STEPS[currentStep].type === "input" && <span className="text-cyan-500 mr-1 sm:mr-2 font-bold">ll&gt;</span>}
            <span className="text-white">{typingText}</span>
            <span className="animate-pulse inline-block w-1.5 sm:w-2 h-3 sm:h-4 bg-white/50 align-middle ml-1" />
          </div>
        )}
      </div>
    </div>
  );
}