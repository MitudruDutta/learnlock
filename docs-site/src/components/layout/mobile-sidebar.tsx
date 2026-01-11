"use client";

import { PanelLeft, Terminal } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Sidebar } from "./sidebar";
import Link from "next/link";
import { useState } from "react";

export function MobileSidebar() {
  const [open, setOpen] = useState(false);

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden h-9 w-9"
        >
          <PanelLeft className="h-5 w-5" />
          <span className="sr-only">Toggle docs navigation</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-[280px] sm:w-[320px] p-0 overflow-y-auto">
        <SheetHeader className="p-4 border-b border-border">
          <SheetTitle>
            <Link 
              href="/" 
              className="flex items-center gap-2"
              onClick={() => setOpen(false)}
            >
              <Terminal className="h-5 w-5 text-primary" />
              <span className="font-bold">learnlock</span>
            </Link>
          </SheetTitle>
        </SheetHeader>
        <div className="p-4" onClick={() => setOpen(false)}>
          <Sidebar />
        </div>
      </SheetContent>
    </Sheet>
  );
}
