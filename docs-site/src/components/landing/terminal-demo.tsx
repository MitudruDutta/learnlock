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
  { text: "/add https://youtu.be/dQw4w9WgXcQ", type: "input", delay: 1000 },
  { 
    text: `[cyan]•[/cyan] Fetching content...
[cyan]•[/cyan] Generating title...
[cyan]•[/cyan] Extracting concepts...
[green]OK[/green] Added: Rick Astley - Never Gonna Give You Up
[green]OK[/green] Added 3 concepts:
  [dim]•[/dim] Rickrolling
  [dim]•[/dim] Bait-and-switch
  [dim]•[/dim] Internet Meme History`, 
    type: "output", 
    delay: 800 
  },
  { text: "/study", type: "input", delay: 1000 },
  { 
    text: `
[bold cyan]Study Session[/bold cyan] — 1 concepts to review

[bold]━━━ 1/1: Rickrolling ━━━[/bold]
[dim]from Rick Astley - Never Gonna Give You Up[/dim]

[cyan]Challenge:[/cyan] Explain the psychological mechanism that makes this bait-and-switch effective.`,
    type: "output", 
    delay: 800 
  },
  { text: "It's just a funny prank where you trick people.", type: "input", delay: 1500 },
  { 
    text: `[yellow]That's a surface-level observation.[/yellow]
WHY is it effective? What specific expectation is being violated?`, 
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
          <div key={i} className="mb-1 whitespace-pre-wrap break-words">
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