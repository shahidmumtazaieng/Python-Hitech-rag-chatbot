"""Chat request/response models."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Chat message request."""
    sessionId: str = Field(..., description="Session identifier from lead submission")
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    context: Optional[str] = Field(None, description="Additional context if needed")


class SourceDocument(BaseModel):
    """Source document from RAG retrieval."""
    content: str = Field(..., description="Document content")
    source: str = Field(..., description="Document source URL or identifier")
    title: Optional[str] = Field(None, description="Document title")
    score: Optional[float] = Field(None, description="Similarity score")


class ChatResponse(BaseModel):
    """Chat message response."""
    response: str = Field(..., description="AI generated response")
    sessionId: str = Field(..., description="Session identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sources: Optional[List[SourceDocument]] = Field(None, description="Source documents used")
    model: str = Field(default="gemini-2.5-flash", description="Model used for generation")


class TalkToHumanRequest(BaseModel):
    """Request to escalate to human agent."""
    sessionId: str = Field(..., description="Session identifier")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes for human agent")
    urgency: str = Field(default="normal", description="Urgency level: low, normal, high")


class TalkToHumanResponse(BaseModel):
    """Response from human escalation request."""
    success: bool
    sessionId: str
    message: str
    estimatedResponseTime: str = Field(default="Within 24 hours")
    ticketId: Optional[str] = None
