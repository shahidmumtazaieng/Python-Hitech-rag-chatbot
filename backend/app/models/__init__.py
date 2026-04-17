"""Pydantic models for the Hitech RAG Chatbot."""
from .lead import LeadCreate, LeadResponse, LeadInDB
from .conversation import Message, Conversation, ConversationCreate
from .chat import ChatRequest, ChatResponse, TalkToHumanRequest

__all__ = [
    "LeadCreate",
    "LeadResponse", 
    "LeadInDB",
    "Message",
    "Conversation",
    "ConversationCreate",
    "ChatRequest",
    "ChatResponse",
    "TalkToHumanRequest",
]
