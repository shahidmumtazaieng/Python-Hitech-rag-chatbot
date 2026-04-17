"use client";

import { Bot } from "lucide-react";

export function TypingIndicator() {
  return (
    <div className="flex gap-3 max-w-[85%]">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#E30613] to-[#C00510] flex items-center justify-center flex-shrink-0">
        <Bot className="w-4 h-4 text-white" />
      </div>
      <div className="bg-gradient-to-br from-[#E30613] to-[#C00510] text-white px-4 py-3 rounded-2xl rounded-bl-md">
        <div className="flex gap-1">
          <span
            className="w-2 h-2 bg-white/60 rounded-full animate-bounce"
            style={{ animationDelay: "0ms" }}
          />
          <span
            className="w-2 h-2 bg-white/60 rounded-full animate-bounce"
            style={{ animationDelay: "150ms" }}
          />
          <span
            className="w-2 h-2 bg-white/60 rounded-full animate-bounce"
            style={{ animationDelay: "300ms" }}
          />
        </div>
      </div>
    </div>
  );
}
