"use client";
import React from 'react'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { AnimatedGroup } from '@/components/ui/animated-group'
import { ContainerScroll } from '@/components/ui/container-scroll-animation'
import { TerminalDemo } from '@/components/landing/terminal-demo'
import { LampEffect } from '@/components/ui/lamp-effect'
import { Variants } from 'framer-motion'

const transitionVariants: { container?: Variants; item?: Variants } = {
    item: {
        hidden: {
            opacity: 0,
            filter: 'blur(12px)',
            y: 12,
        },
        visible: {
            opacity: 1,
            filter: 'blur(0px)',
            y: 0,
            transition: {
                type: 'spring',
                bounce: 0.3,
                duration: 1.5,
            },
        },
    },
}

export function HeroSection() {
    return (
        <main id="hero" className="overflow-hidden bg-[#18181b]">
            <section>
                <div className="relative pt-24 md:pt-36">
                    {/* Lamp Effect Background */}
                    <LampEffect />
                    
                    <div className="mx-auto max-w-7xl px-6 relative z-10">
                        <div className="text-center sm:mx-auto lg:mr-auto lg:mt-0">
                            <AnimatedGroup variants={transitionVariants}>
                                <Link
                                    href="/docs/installation"
                                    className="hover:bg-[#1f1f23] bg-[#27272a] group mx-auto flex w-fit items-center gap-4 rounded-full border border-[#3f3f46] p-1 pl-4 shadow-md shadow-black/10 transition-all duration-300">
                                    <span className="text-foreground text-sm">v0.1.0 is now available</span>
                                    <span className="block h-4 w-0.5 bg-[#3f3f46]"></span>
                                    <div className="bg-[#18181b] group-hover:bg-[#27272a] size-6 overflow-hidden rounded-full duration-500">
                                        <div className="flex w-12 -translate-x-1/2 duration-500 ease-in-out group-hover:translate-x-0">
                                            <span className="flex size-6">
                                                <ArrowRight className="m-auto size-3" />
                                            </span>
                                            <span className="flex size-6">
                                                <ArrowRight className="m-auto size-3" />
                                            </span>
                                        </div>
                                    </div>
                                </Link>
                    
                                <h1 className="mt-8 max-w-4xl mx-auto text-balance text-5xl sm:text-6xl md:text-7xl lg:mt-16 xl:text-[5.25rem] font-bold tracking-tight">
                                    The app that <br className="hidden sm:inline" />
                                    <span className="text-green-500">
                                        argues with you.
                                    </span>
                                </h1>
                                <p className="mx-auto mt-8 max-w-2xl text-balance text-lg text-[#a1a1aa]">
                                    Stop fooling yourself. LearnLock uses adversarial Socratic dialogue to expose what you don&apos;t actually understand. It infers your beliefs, finds contradictions, and attacks until you get it right.
                                </p>
                            </AnimatedGroup>
                        </div>
                    </div>

                    <div className="relative mt-8 overflow-hidden px-2 sm:mt-12 md:mt-20">
                        <ContainerScroll
                            titleComponent={
                                <h1 className="text-4xl font-semibold text-white">
                                    Don&apos;t just read. <br />
                                    <span className="text-4xl md:text-[6rem] font-bold mt-1 leading-none">
                                        Engage.
                                    </span>
                                </h1>
                            }
                        >
                            <TerminalDemo />
                        </ContainerScroll>
                    </div>
                </div>
            </section>
        </main>
    )
}
