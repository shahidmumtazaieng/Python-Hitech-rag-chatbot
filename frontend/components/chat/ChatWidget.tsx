"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Phone, X, MessageCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { LeadForm } from "./LeadForm";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import { ChatInput } from "./ChatInput";
import { 
  submitLead, 
  sendMessage, 
  talkToHuman, 
  restoreSession,
  checkSession,
  LeadData,
  Message 
} from "@/lib/api";

interface ChatWidgetProps {
  isOpen?: boolean;
  onClose?: () => void;
  embedded?: boolean;
}

const SESSION_KEY = "hitech_chat_session";
const SESSION_TTL = 24 * 60 * 60 * 1000; // 24 hours

export function ChatWidget({ isOpen: controlledOpen, onClose, embedded = false }: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(controlledOpen || false);
  const [hasSubmittedLead, setHasSubmittedLead] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [leadInfo, setLeadInfo] = useState<any>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isRestoring, setIsRestoring] = useState(false);
  const [isEscalated, setIsEscalated] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Convert API messages to local format
  const convertApiMessages = (apiMessages: any[]): Message[] => {
    return apiMessages.map(msg => ({
      role: msg.role as "user" | "assistant" | "system",
      content: msg.content,
      timestamp: msg.timestamp || new Date().toISOString(),
      sources: msg.sources,
      metadata: msg.metadata,
    }));
  };

  // Restore session from backend
  const restoreSessionFromBackend = useCallback(async (savedSessionId: string) => {
    setIsRestoring(true);
    try {
      // First check if session is still valid
      const checkResult = await checkSession(savedSessionId);
      
      if (!checkResult.valid) {
        console.log("Session expired or invalid, clearing localStorage");
        localStorage.removeItem(SESSION_KEY);
        setIsRestoring(false);
        return false;
      }

      // Restore full session with messages
      const result = await restoreSession(savedSessionId);
      
      if (result.success && result.sessionId) {
        setSessionId(result.sessionId);
        setLeadInfo(result.lead);
        setHasSubmittedLead(true);
        setIsEscalated(result.isEscalated);
        
        if (result.messages && result.messages.length > 0) {
          setMessages(convertApiMessages(result.messages));
        }
        
        // Update localStorage with fresh data
        const sessionData = {
          sessionId: result.sessionId,
          leadInfo: result.lead,
          messages: result.messages,
          timestamp: Date.now(),
        };
        localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
        
        console.log("Session restored successfully:", result.sessionId);
        return true;
      } else {
        console.log("Session restoration failed:", result.message);
        localStorage.removeItem(SESSION_KEY);
        return false;
      }
    } catch (error) {
      console.error("Failed to restore session:", error);
      localStorage.removeItem(SESSION_KEY);
      return false;
    } finally {
      setIsRestoring(false);
    }
  }, []);

  // Load session from localStorage on mount and validate with backend
  useEffect(() => {
    const initSession = async () => {
      const saved = localStorage.getItem(SESSION_KEY);
      if (saved) {
        try {
          const sessionData = JSON.parse(saved);
          const age = Date.now() - (sessionData.timestamp || 0);
          
          if (age < SESSION_TTL && sessionData.sessionId) {
            // Validate and restore from backend
            await restoreSessionFromBackend(sessionData.sessionId);
          } else {
            console.log("Local session expired, clearing");
            localStorage.removeItem(SESSION_KEY);
          }
        } catch (e) {
          console.error("Failed to load session:", e);
          localStorage.removeItem(SESSION_KEY);
        }
      }
    };
    
    initSession();
  }, [restoreSessionFromBackend]);

  // Save session to localStorage
  const saveSession = useCallback(() => {
    if (sessionId && leadInfo) {
      const sessionData = {
        sessionId,
        leadInfo,
        messages,
        timestamp: Date.now(),
      };
      localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
    }
  }, [sessionId, leadInfo, messages]);

  useEffect(() => {
    saveSession();
  }, [saveSession]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleLeadSubmit = async (data: LeadData) => {
    setIsLoading(true);
    try {
      const response = await submitLead(data);
      if (response.success) {
        setSessionId(response.sessionId);
        setLeadInfo(response.lead);
        setHasSubmittedLead(true);
        
        // Add welcome message
        setMessages([
          {
            role: "assistant",
            content: `Hello ${data.fullName.split(" ")[0]}! Welcome to Hitech Steel Industries. How can I help you today?`,
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    } catch (error: any) {
      console.error("Failed to submit lead:", error);
      const errorMessage = error?.response?.data?.detail 
        || error?.message 
        || "Failed to submit. Please try again.";
      
      if (errorMessage.includes("Network Error")) {
        alert("Cannot connect to server. Please make sure the backend is running on http://127.0.0.1:8000");
      } else {
        alert(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!sessionId) return;

    // Add user message
    const userMessage: Message = {
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const response = await sendMessage(sessionId, content);
      
      const assistantMessage: Message = {
        role: "assistant",
        content: response.response,
        timestamp: response.timestamp,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Failed to send message:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "I apologize, but I'm having trouble responding right now. Please try again or click 'Talk to Human' for assistance.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleTalkToHuman = async () => {
    if (!sessionId) return;
    
    const confirmed = window.confirm(
      "Would you like to speak with a human representative? We'll forward your conversation to our team."
    );
    
    if (!confirmed) return;

    setIsTyping(true);
    try {
      await talkToHuman(sessionId, "Customer requested human agent");
      setIsEscalated(true);
      
      const escalationMessage: Message = {
        role: "assistant",
        content: "Your request has been forwarded to our team. A representative will contact you shortly at the phone number you provided. Thank you for your patience!",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, escalationMessage]);
    } catch (error) {
      console.error("Failed to escalate:", error);
      alert("Failed to forward request. Please try again.");
    } finally {
      setIsTyping(false);
    }
  };

  const toggleChat = () => {
    const newOpen = !isOpen;
    setIsOpen(newOpen);
    if (!newOpen && onClose) {
      onClose();
    }
  };

  // Widget content
  const renderContent = () => {
    // Show loading while restoring session
    if (isRestoring) {
      return (
        <div className="flex-1 flex flex-col items-center justify-center p-8">
          <Loader2 className="w-8 h-8 animate-spin text-[#E30613] mb-4" />
          <p className="text-gray-600 text-sm">Restoring your conversation...</p>
        </div>
      );
    }

    if (!hasSubmittedLead) {
      return (
        <div className="p-4 overflow-y-auto">
          <LeadForm onSubmit={handleLeadSubmit} isLoading={isLoading} />
        </div>
      );
    }

    return (
      <>
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
          {messages.length === 0 && (
            <div className="bg-white rounded-xl p-4 border-l-4 border-[#E30613] shadow-sm">
              <h4 className="font-semibold text-gray-900 mb-1">Welcome to Hitech Steel Industries!</h4>
              <p className="text-sm text-gray-600">
                Hello! I'm your AI assistant. I can help you with information about our steel products, services, and answer any questions you may have.
              </p>
            </div>
          )}
          {messages
            .filter(msg => msg.role !== "system")
            .map((message, index) => (
              <MessageBubble key={index} message={message} />
            ))}
          {isTyping && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Talk to Human Button */}
        {!isEscalated && (
          <div className="px-4 py-2 bg-gray-50 border-t">
            <Button
              variant="outline"
              onClick={handleTalkToHuman}
              disabled={isTyping}
              className="w-full border-[#003087] text-[#003087] hover:bg-[#003087] hover:text-white"
            >
              <Phone className="w-4 h-4 mr-2" />
              Talk to Human
            </Button>
          </div>
        )}

        {/* Input */}
        <ChatInput
          onSend={handleSendMessage}
          disabled={isTyping || isEscalated}
          placeholder={isEscalated ? "Conversation ended - A representative will contact you" : "Type your message..."}
        />
      </>
    );
  };

  // Floating widget
  if (!embedded) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        {/* Chat Window */}
        {isOpen && (
          <div className="mb-4 w-[380px] h-[600px] bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col border">
            {/* Header */}
            <div className="bg-gradient-to-r from-[#E30613] to-[#C00510] text-white p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold">Hitech Assistant</h3>
                  <p className="text-xs text-white/80">Online</p>
                </div>
              </div>
              <button
                onClick={toggleChat}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
              {renderContent()}
            </div>
          </div>
        )}

        {/* Toggle Button */}
        <button
          onClick={toggleChat}
          className="w-14 h-14 bg-gradient-to-r from-[#E30613] to-[#C00510] rounded-full shadow-lg flex items-center justify-center hover:scale-105 transition-transform"
        >
          {isOpen ? (
            <X className="w-6 h-6 text-white" />
          ) : (
            <MessageCircle className="w-6 h-6 text-white" />
          )}
        </button>
      </div>
    );
  }

  // Embedded version (full page)
  return (
    <div className="w-full h-full bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#E30613] to-[#C00510] text-white p-4 flex items-center gap-3">
        <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
          <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
        </div>
        <div>
          <h3 className="font-semibold">Hitech Assistant</h3>
          <p className="text-xs text-white/80">Online</p>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {renderContent()}
      </div>
    </div>
  );
}
