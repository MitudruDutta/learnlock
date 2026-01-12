"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { docsNav } from "@/lib/docs-nav";
import { motion } from "motion/react";
import {
  BookOpen,
  Download,
  Zap,
  Brain,
  MessageSquare,
  Clock,
  Play,
  Plus,
  Eye,
  Terminal,
  Settings,
  Swords,
} from "lucide-react";

const iconMap: Record<string, React.ReactNode> = {
  "Introduction": <BookOpen className="h-4 w-4" />,
  "Installation": <Download className="h-4 w-4" />,
  "Quickstart": <Zap className="h-4 w-4" />,
  "Adversarial Learning": <Brain className="h-4 w-4" />,
  "Socratic Dialogue": <MessageSquare className="h-4 w-4" />,
  "Spaced Repetition": <Clock className="h-4 w-4" />,
  "Duel Engine": <Swords className="h-4 w-4" />,
  "Study Sessions": <Play className="h-4 w-4" />,
  "Adding Content": <Plus className="h-4 w-4" />,
  "OCR & Images": <Eye className="h-4 w-4" />,
  "CLI Commands": <Terminal className="h-4 w-4" />,
  "Configuration": <Settings className="h-4 w-4" />,
};

export function Sidebar() {
  const pathname = usePathname();

  return (
    <nav className="w-full pb-20">
      {docsNav.map((section, sectionIndex) => (
        <motion.div
          key={sectionIndex}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: sectionIndex * 0.1 }}
          className="pb-6"
        >
          <h4 className="mb-3 px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            {section.title}
          </h4>
          {section.items?.length && (
            <div className="grid grid-flow-row auto-rows-max text-sm gap-1">
              {section.items.map((item, itemIndex) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={itemIndex}
                    href={item.href}
                    className={cn(
                      "group flex w-full items-center gap-3 rounded-lg px-3 py-2 transition-all duration-200",
                      isActive
                        ? "bg-accent text-foreground border-l-2 border-foreground"
                        : "text-muted-foreground hover:text-foreground hover:bg-accent/50 border-l-2 border-transparent"
                    )}
                  >
                    <span
                      className={cn(
                        "shrink-0 transition-colors duration-200",
                        isActive
                          ? "text-foreground"
                          : "text-muted-foreground group-hover:text-foreground"
                      )}
                    >
                      {iconMap[item.title] || <BookOpen className="h-4 w-4" />}
                    </span>
                    <span className="group-hover:translate-x-0.5 transition-transform duration-200">
                      {item.title}
                    </span>
                  </Link>
                );
              })}
            </div>
          )}
        </motion.div>
      ))}
    </nav>
  );
}
