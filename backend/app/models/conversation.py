"""Conversation data models."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role types."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Individual message in a conversation."""
    role: MessageRole = Field(..., description="Message sender role")
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(None, description="Additional message metadata")


class ConversationBase(BaseModel):
    """Base conversation model."""
    sessionId: str = Field(..., description="Associated lead session ID")
    leadInfo: Optional[dict] = Field(None, description="Snapshot of lead information")


class ConversationCreate(ConversationBase):
    """Model for creating a new conversation."""
    messages: List[Message] = Field(default_factory=list)


class Conversation(ConversationBase):
    """Full conversation model."""
    id: Optional[str] = Field(None, alias="_id")
    messages: List[Message] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    isEscalated: bool = Field(default=False, description="Whether conversation was escalated to human")
    escalationNotes: Optional[str] = Field(None, description="Notes from escalation")
    
    class Config:
        populate_by_name = True


class ConversationUpdate(BaseModel):
    """Model for updating a conversation."""
    messages: Optional[List[Message]] = None
    isEscalated: Optional[bool] = None
    escalationNotes: Optional[str] = None
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
