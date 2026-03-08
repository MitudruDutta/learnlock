"use client";
import React, { useEffect, useState } from "react";
import { ArrowRight, Book, Github, Menu, Terminal, Zap } from "lucide-react";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetClose,
} from "@/components/ui/sheet";
import Link from "next/link";

interface MenuItem {
  title: string;
  url: string;
  description?: string;
  icon?: React.ReactNode;
  items?: MenuItem[];
}

interface NavbarProps {
  logo?: {
    url: string;
    title: string;
  };
  menu?: MenuItem[];
  mobileExtraLinks?: {
    name: string;
    url: string;
  }[];
}

const handleLogoClick = (e: React.MouseEvent<HTMLAnchorElement>, url: string) => {
  if (url.startsWith('/#')) {
    e.preventDefault();
    const element = document.getElementById(url.slice(2));
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
      window.location.href = url;
    }
  }
};

export const Navbar = ({
  logo = {
    url: "/#hero",
    title: "learnlock",
  },
  menu = [
    { title: "Home", url: "/" },
    {
      title: "Documentation",
      url: "/docs",
      items: [
        {
          title: "Introduction",
          description: "Get started with LearnLock",
          icon: <Book className="size-5 shrink-0" />,
          url: "/docs",
        },
        {
          title: "Installation",
          description: "Install via pip or script",
          icon: <Terminal className="size-5 shrink-0" />,
          url: "/docs/installation",
        },
        {
          title: "Core Concepts",
          description: "Understand Socratic dialogue and spaced repetition",
          icon: <Zap className="size-5 shrink-0" />,
          url: "/docs/socratic-dialogue",
        },
        {
          title: "Reference",
          description: "CLI commands and configuration",
          icon: <Menu className="size-5 shrink-0" />,
          url: "/docs/commands",
        },
      ],
    },
  ],
  mobileExtraLinks = [],
}: NavbarProps) => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };

    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <section className="sticky top-0 z-50 pointer-events-none">
      <div className="container mx-auto px-4 pt-4">
        <div
          className={`pointer-events-auto flex items-center justify-between rounded-2xl border border-white/10 bg-[#18181b]/60 backdrop-blur-xl transition-all duration-300 ${
            scrolled ? "shadow-lg bg-[#18181b]/75 border-white/20" : "shadow-sm"
          }`}
        >
          <nav className="hidden lg:flex w-full items-center justify-between px-4 py-3">
            <div className="flex items-center gap-6">
              <Link 
                href={logo.url} 
                className="flex items-center gap-2"
                onClick={(e) => handleLogoClick(e, logo.url)}
              >
                <Terminal className="h-6 w-6 text-foreground" />
                <span className="text-lg font-bold tracking-tight">
                  {logo.title}
                </span>
              </Link>
              <NavigationMenu className="transition-all duration-200 ease-out">
                <NavigationMenuList>
                  {menu.map((item) => renderMenuItem(item))}
                </NavigationMenuList>
              </NavigationMenu>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="https://github.com/MitudruDutta/learnlock"
                target="_blank"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <Github className="h-5 w-5" />
              </Link>
              <Link
                href="/docs/installation"
                className="group relative flex h-10 w-36 cursor-pointer items-center justify-center overflow-hidden rounded-full border border-[#27272a] bg-background p-2 text-center text-sm font-semibold"
              >
                <span className="inline-block translate-x-1 transition-all duration-300 group-hover:translate-x-12 group-hover:opacity-0">
                  Get Started
                </span>
                <div className="absolute top-0 z-10 flex h-full w-full translate-x-12 items-center justify-center gap-2 text-primary-foreground opacity-0 transition-all duration-300 group-hover:-translate-x-1 group-hover:opacity-100">
                  <span>Get Started</span>
                  <ArrowRight className="h-4 w-4" />
                </div>
                <div className="absolute left-[20%] top-[40%] h-2 w-2 scale-[1] rounded-lg bg-primary transition-all duration-300 group-hover:left-[0%] group-hover:top-[0%] group-hover:h-full group-hover:w-full group-hover:scale-[1.8] group-hover:bg-primary"></div>
              </Link>
            </div>
          </nav>

          <div className="block w-full lg:hidden px-4 py-3">
            <div className="flex items-center justify-between">
              <Link 
                href={logo.url} 
                className="flex items-center gap-2"
                onClick={(e) => handleLogoClick(e, logo.url)}
              >
                <Terminal className="h-6 w-6 text-foreground" />
                <span className="text-lg font-bold tracking-tight">
                  {logo.title}
                </span>
              </Link>
              <Sheet>
                <SheetTrigger asChild>
                  <Button
                    variant="outline"
                    size="icon"
                    className="border-[#27272a] bg-black/20"
                  >
                    <Menu className="size-4" />
                  </Button>
                </SheetTrigger>
                <SheetContent
                  className="overflow-y-auto flex flex-col transition-all duration-300 ease-out
                  border border-white/15 bg-[#18181b]/60 backdrop-blur-xl
                  rounded-l-3xl my-2 mr-2 h-[calc(100vh-1rem)] w-full max-w-sm shadow-xl"
                >
                  <SheetHeader>
                    <SheetTitle>
                      <Link 
                        href={logo.url} 
                        className="flex items-center gap-2"
                        onClick={(e) => handleLogoClick(e, logo.url)}
                      >
                        <Terminal className="h-6 w-6 text-foreground" />
                        <span className="text-lg font-bold tracking-tight">
                          {logo.title}
                        </span>
                      </Link>
                    </SheetTitle>
                  </SheetHeader>
                  <div className="flex-1 my-6 flex flex-col">
                    <Accordion
                      type="single"
                      collapsible
                      className="flex w-full flex-col gap-4"
                    >
                      {menu.map((item) => renderMobileMenuItem(item))}
                    </Accordion>
                    {mobileExtraLinks.length > 0 && (
                      <div className="border-t border-[#27272a] py-4 mt-4">
                        <div className="grid grid-cols-2 justify-start">
                          {mobileExtraLinks.map((link, idx) => (
                            <SheetClose asChild key={idx}>
                              <Link
                                className="inline-flex h-10 items-center gap-2 whitespace-nowrap rounded-md px-4 py-2 text-sm font-medium text-muted-foreground transition-all duration-200 ease-out hover:bg-[#27272a] hover:text-foreground"
                                href={link.url}
                              >
                                {link.name}
                              </Link>
                            </SheetClose>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col gap-3 mt-auto border-t border-[#27272a] pt-6">
                    <SheetClose asChild>
                      <Button asChild className="transition-all duration-200">
                        <Link href="/docs/installation">Get Started</Link>
                      </Button>
                    </SheetClose>
                    <SheetClose asChild>
                      <Button
                        asChild
                        variant="outline"
                        className="border-[#27272a] transition-all duration-200 hover:bg-[#27272a]"
                      >
                        <Link
                          href="https://github.com/MitudruDutta/learnlock"
                          target="_blank"
                        >
                          <Github className="mr-2 h-4 w-4" />
                          View on GitHub
                        </Link>
                      </Button>
                    </SheetClose>
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

const renderMenuItem = (item: MenuItem) => {
  if (item.items) {
    return (
      <NavigationMenuItem key={item.title} className="text-muted-foreground">
        <NavigationMenuTrigger className="transition-all duration-200 ease-out data-[state=open]:scale-[1.02]">
          {item.title}
        </NavigationMenuTrigger>
        <NavigationMenuContent>
          <ul className="w-80 p-3 bg-[#1f1f23]">
            {item.items.map((subItem) => (
              <li key={subItem.title}>
                <NavigationMenuLink asChild>
                  <Link
                    className="flex select-none gap-4 rounded-md p-3 leading-none no-underline outline-none transition-all duration-200 ease-out hover:bg-[#27272a] hover:text-foreground"
                    href={subItem.url}
                  >
                    {subItem.icon}
                    <div>
                      <div className="text-sm font-semibold">
                        {subItem.title}
                      </div>
                      {subItem.description && (
                        <p className="text-sm leading-snug text-muted-foreground">
                          {subItem.description}
                        </p>
                      )}
                    </div>
                  </Link>
                </NavigationMenuLink>
              </li>
            ))}
          </ul>
        </NavigationMenuContent>
      </NavigationMenuItem>
    );
  }

  return (
    <Link
      key={item.title}
      className="group inline-flex h-9 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium text-muted-foreground transition-all duration-300 ease-out hover:bg-[#27272a] hover:text-foreground focus-visible:ring-1 focus-visible:ring-offset-0"
      href={item.url}
    >
      {item.title}
    </Link>
  );
};

const renderMobileMenuItem = (item: MenuItem) => {
  if (item.items) {
    return (
      <AccordionItem key={item.title} value={item.title} className="border-b-0">
        <AccordionTrigger className="py-0 font-semibold hover:no-underline transition-all duration-200 ease-out">
          {item.title}
        </AccordionTrigger>
        <AccordionContent className="mt-2">
          {item.items.map((subItem) => (
            <SheetClose asChild key={subItem.title}>
              <Link
                className="flex select-none gap-4 rounded-md p-3 leading-none outline-none transition-all duration-250 ease-out hover:bg-[#27272a] hover:text-foreground"
                href={subItem.url}
              >
                {subItem.icon}
                <div>
                  <div className="text-sm font-semibold">{subItem.title}</div>
                  {subItem.description && (
                    <p className="text-sm leading-snug text-muted-foreground">
                      {subItem.description}
                    </p>
                  )}
                </div>
              </Link>
            </SheetClose>
          ))}
        </AccordionContent>
      </AccordionItem>
    );
  }

  return (
    <SheetClose asChild key={item.title}>
      <Link href={item.url} className="font-semibold transition-all duration-200 ease-out hover:text-foreground">
        {item.title}
      </Link>
    </SheetClose>
  );
};
