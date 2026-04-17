"use client";

import { useState, useRef, KeyboardEvent } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, disabled, placeholder }: ChatInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        120
      )}px`;
    }
  };

  return (
    <div className="flex gap-2 items-end p-4 bg-white border-t">
      <textarea
        ref={textareaRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        onInput={handleInput}
        placeholder={placeholder || "Type your message..."}
        disabled={disabled}
        rows={1}
        className="flex-1 min-h-[48px] max-h-[120px] px-4 py-3 text-sm bg-gray-50 border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-[#E30613]/20 focus:border-[#E30613] disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <Button
        onClick={handleSend}
        disabled={disabled || !message.trim()}
        className="h-12 w-12 rounded-xl bg-gradient-to-r from-[#E30613] to-[#C00510] hover:opacity-90 disabled:opacity-50 p-0"
      >
        <Send className="w-5 h-5" />
      </Button>
    </div>
  );
}
