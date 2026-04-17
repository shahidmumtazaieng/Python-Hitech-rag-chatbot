// API client for Hitech Chatbot backend
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
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

export async function getConversation(sessionId: string) {
  const response = await api.get(`/api/conversation/${sessionId}`);
  return response.data;
}

export async function getHealth() {
  const response = await api.get('/api/health');
  return response.data;
}

export default api;
