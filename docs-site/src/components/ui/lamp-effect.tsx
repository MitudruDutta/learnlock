"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface LampEffectProps {
  className?: string
}

export function LampEffect({ className }: LampEffectProps) {
  return (
    <div className={cn("absolute top-0 isolate z-0 flex w-full flex-1 items-start justify-center", className)}>
      {/* Blur overlay */}
      <div className="absolute top-0 z-50 h-64 w-full bg-transparent opacity-10 backdrop-blur-md" />

      {/* Main glow */}
      <div className="absolute inset-auto z-50 h-56 w-[22rem] md:w-[45rem] -translate-y-[-30%] rounded-full bg-green-500/50 opacity-80 blur-[100px]" />

      {/* Lamp effect */}
      <motion.div
        initial={{ width: "8rem" }}
        viewport={{ once: true }}
        transition={{ ease: "easeInOut", delay: 0.3, duration: 0.8 }}
        whileInView={{ width: "clamp(18rem, 30vw, 30rem)" }}
        className="absolute top-0 z-30 h-48 -translate-y-[20%] rounded-full bg-green-500/50 blur-3xl"
      />

      {/* Top line */}
      <motion.div
        initial={{ width: "10rem" }}
        viewport={{ once: true }}
        transition={{ ease: "easeInOut", delay: 0.3, duration: 0.8 }}
        whileInView={{ width: "clamp(22rem, 60vw, 45rem)" }}
        className="absolute inset-auto z-50 h-1 -translate-y-[-10%] bg-green-500/70"
      />

      {/* Left gradient cone */}
      <motion.div
        initial={{ opacity: 0.5, width: "15rem" }}
        whileInView={{ opacity: 1, width: "clamp(22rem, 50vw, 45rem)" }}
        transition={{
          delay: 0.3,
          duration: 0.8,
          ease: "easeInOut",
        }}
        style={{
          backgroundImage: `conic-gradient(var(--conic-position), var(--tw-gradient-stops))`,
        }}
        className="absolute inset-auto right-1/2 h-72 overflow-visible w-[22rem] md:w-[45rem] bg-gradient-conic from-green-500/50 via-transparent to-transparent [--conic-position:from_70deg_at_center_top]"
      >
        <div className="absolute w-[100%] left-0 bg-[#18181b] h-56 bottom-0 z-20 [mask-image:linear-gradient(to_top,white,transparent)]" />
        <div className="absolute w-56 h-[100%] left-0 bg-[#18181b] bottom-0 z-20 [mask-image:linear-gradient(to_right,white,transparent)]" />
      </motion.div>

      {/* Right gradient cone */}
      <motion.div
        initial={{ opacity: 0.5, width: "15rem" }}
        whileInView={{ opacity: 1, width: "clamp(22rem, 50vw, 45rem)" }}
        transition={{
          delay: 0.3,
          duration: 0.8,
          ease: "easeInOut",
        }}
        style={{
          backgroundImage: `conic-gradient(var(--conic-position), var(--tw-gradient-stops))`,
        }}
        className="absolute inset-auto left-1/2 h-72 w-[22rem] md:w-[45rem] bg-gradient-conic from-transparent via-transparent to-green-500/50 [--conic-position:from_290deg_at_center_top]"
      >
        <div className="absolute w-56 h-[100%] right-0 bg-[#18181b] bottom-0 z-20 [mask-image:linear-gradient(to_left,white,transparent)]" />
        <div className="absolute w-[100%] right-0 bg-[#18181b] h-56 bottom-0 z-20 [mask-image:linear-gradient(to_top,white,transparent)]" />
      </motion.div>
    </div>
  )
}
