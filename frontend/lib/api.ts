// API client for Hitech Chatbot backend
import axios from 'axios';

// Use local proxy to avoid CORS issues
const API_URL = typeof window !== 'undefined' ? '/api' : (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000');

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Types
export interface LeadData {
  fullName: string;
  email: string;
  phone: string;
  company?: string;
  inquiryType?: string;
}

export interface LeadResponse {
  success: boolean;
  sessionId: string;
  message: string;
  lead?: LeadData & { sessionId: string; createdAt: string };
}

export interface ChatRequest {
  sessionId: string;
  message: string;
}

export interface ChatResponse {
  response: string;
  sessionId: string;
  timestamp: string;
  sources?: Array<{
    content: string;
    source: string;
    title?: string;
    score?: number;
  }>;
  model: string;
}

export interface TalkToHumanRequest {
  sessionId: string;
  notes?: string;
}

export interface TalkToHumanResponse {
  success: boolean;
  sessionId: string;
  message: string;
  estimatedResponseTime?: string;
  ticketId?: string;
}

export interface Message {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: Array<{
    content: string;
    source: string;
    title?: string;
    score?: number;
  }>;
  metadata?: Record<string, any>;
  timestamp?: string;
}

export interface SessionRestoreRequest {
  sessionId: string;
}

export interface SessionRestoreResponse {
  success: boolean;
  sessionId?: string;
  lead?: LeadData & { 
    sessionId: string; 
    createdAt: string;
    status?: string;
    source?: string;
  };
  messages: Message[];
  isEscalated: boolean;
  message: string;
}

export interface SessionCheckRequest {
  sessionId: string;
}

export interface SessionCheckResponse {
  valid: boolean;
  sessionId?: string;
  lead?: LeadData & { 
    sessionId: string; 
    createdAt: string;
    status?: string;
  };
  expiresAt?: string;
}

export interface ConversationSummary {
  lead: LeadData & { 
    sessionId: string; 
    createdAt: string;
    status?: string;
    source?: string;
  };
  conversation: {
    id?: string;
    sessionId: string;
    isEscalated: boolean;
    escalationNotes?: string;
    escalationTime?: string;
    lastMessageAt?: string;
    messageCount: number;
    createdAt: string;
    updatedAt: string;
  };
  messages: Message[];
  hasActiveSession: boolean;
}

// API Functions
export async function submitLead(leadData: LeadData): Promise<LeadResponse> {
  const response = await api.post('/api/lead', leadData);
  return response.data;
}

export async function sendMessage(sessionId: string, message: string): Promise<ChatResponse> {
  const response = await api.post('/api/chat/sync', {
    sessionId,
    message,
  });
  return response.data;
}

export async function talkToHuman(sessionId: string, notes?: string): Promise<TalkToHumanResponse> {
  const response = await api.post('/api/talk-to-human', {
    sessionId,
    notes,
  });
  return response.data;
}

export async function restoreSession(sessionId: string): Promise<SessionRestoreResponse> {
  const response = await api.post('/api/session/restore', {
    sessionId,
  });
  return response.data;
}

export async function checkSession(sessionId: string): Promise<SessionCheckResponse> {
  const response = await api.post('/api/session/check', {
    sessionId,
  });
  return response.data;
}

export async function getConversation(sessionId: string): Promise<ConversationSummary> {
  const response = await api.get(`/api/conversation/${sessionId}`);
  return response.data;
}

export async function getHealth() {
  const response = await api.get('/api/health');
  return response.data;
}

export default api;
