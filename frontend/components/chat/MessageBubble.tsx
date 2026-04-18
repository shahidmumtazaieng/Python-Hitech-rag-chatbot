"use client";

import { User, Bot, Info } from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string;
}

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";
  
  const formatTime = () => {
    if (!message.timestamp) {
      return new Date().toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      });
    }
    return new Date(message.timestamp).toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  };

  // Convert URLs to links
  const formatContent = (content: string) => {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return content.replace(
      urlRegex,
      '<a href="$1" target="_blank" rel="noopener noreferrer" class="underline hover:text-blue-300">$1</a>'
    );
  };

  // System messages are rendered differently (centered, smaller)
  if (isSystem) {
    return (
      <div className="flex justify-center my-2">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-full text-xs text-gray-500">
          <Info className="w-3 h-3" />
          <span dangerouslySetInnerHTML={{ __html: formatContent(message.content) }} />
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex gap-3 max-w-[85%]",
        isUser ? "ml-auto flex-row-reverse" : ""
      )}
    >
      <div
        className={cn(
          "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
          isUser ? "bg-[#003087]" : "bg-gradient-to-br from-[#E30613] to-[#C00510]"
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>
      <div className={cn("flex flex-col", isUser ? "items-end" : "items-start")}>
        <div
          className={cn(
            "px-4 py-2.5 rounded-2xl text-sm leading-relaxed",
            isUser
              ? "bg-white text-gray-900 rounded-br-md shadow-sm border"
              : "bg-gradient-to-br from-[#E30613] to-[#C00510] text-white rounded-bl-md"
          )}
          dangerouslySetInnerHTML={{ __html: formatContent(message.content) }}
        />
        <span className="text-xs text-gray-400 mt-1 px-1">{formatTime()}</span>
      </div>
    </div>
  );
}
