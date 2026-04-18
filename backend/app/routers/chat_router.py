"""Chat router for message handling."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.models.chat import ChatRequest, ChatResponse, TalkToHumanRequest, TalkToHumanResponse
from app.models.conversation import MessageRole
from app.services.postgresql_service import PostgreSQLService, get_postgresql_service
from app.services.rag_service import RAGService, get_rag_service

router = APIRouter(prefix="/api", tags=["chat"])


# Request/Response models for session management
class SessionRestoreRequest(BaseModel):
    """Request to restore a session."""
    sessionId: str = Field(..., description="Session identifier to restore")


class SessionRestoreResponse(BaseModel):
    """Response for session restoration."""
    success: bool
    sessionId: Optional[str] = None
    lead: Optional[Dict[str, Any]] = None
    messages: List[Dict[str, Any]] = []
    isEscalated: bool = False
    message: str = ""


class SessionCheckRequest(BaseModel):
    """Request to check session validity."""
    sessionId: str = Field(..., description="Session identifier to check")


class SessionCheckResponse(BaseModel):
    """Response for session check."""
    valid: bool
    sessionId: Optional[str] = None
    lead: Optional[Dict[str, Any]] = None
    expiresAt: Optional[str] = None


@router.post("/chat/sync", response_model=ChatResponse)
async def chat_sync(
    request: ChatRequest,
    postgresql: PostgreSQLService = Depends(get_postgresql_service),
    rag: RAGService = Depends(get_rag_service)
) -> ChatResponse:
    """
    Synchronous chat endpoint with RAG.
    
    - Validates session
    - Retrieves conversation history
    - Runs RAG pipeline
    - Stores messages
    - Returns AI response
    """
    try:
        # Validate session
        lead = await postgresql.get_lead_by_session(request.sessionId)
        if not lead:
            raise HTTPException(
                status_code=404,
                detail="Session not found. Please submit lead form first."
            )
        
        # Check if conversation is escalated
        conversation = await postgresql.get_conversation(request.sessionId)
        if conversation and conversation.get('isEscalated'):
            return ChatResponse(
                response="This conversation has been escalated to a human representative. They will contact you shortly.",
                sessionId=request.sessionId,
                model="system"
            )
        
        # Process chat with RAG
        response = await rag.process_chat(request, lead)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing error: {str(e)}"
        )


@router.post("/talk-to-human", response_model=TalkToHumanResponse)
async def talk_to_human(
    request: TalkToHumanRequest,
    postgresql: PostgreSQLService = Depends(get_postgresql_service),
    rag: RAGService = Depends(get_rag_service)
) -> TalkToHumanResponse:
    """
    Escalate conversation to human agent.
    
    - Marks conversation as escalated
    - Stores escalation notes
    - Returns confirmation
    """
    try:
        # Validate session
        lead = await postgresql.get_lead_by_session(request.sessionId)
        if not lead:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        # Get conversation summary for notes
        summary = await rag.get_conversation_summary(request.sessionId)
        full_notes = f"{request.notes or ''}\n\n{summary}".strip()
        
        # Escalate conversation
        success = await postgresql.escalate_to_human(
            request.sessionId,
            notes=full_notes
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to escalate conversation"
            )
        
        # Add system message about escalation
        await postgresql.add_message(
            session_id=request.sessionId,
            role=MessageRole.SYSTEM,
            content="Conversation escalated to human agent.",
            metadata={"escalation_notes": request.notes}
        )
        
        return TalkToHumanResponse(
            success=True,
            sessionId=request.sessionId,
            message="Your request has been forwarded to our team. A representative will contact you shortly.",
            ticketId=request.sessionId[:8].upper()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Escalation error: {str(e)}"
        )


@router.post("/session/restore", response_model=SessionRestoreResponse)
async def restore_session(
    request: SessionRestoreRequest,
    rag: RAGService = Depends(get_rag_service)
) -> SessionRestoreResponse:
    """
    Restore a previous chat session.
    
    - Validates session exists and is not expired
    - Returns lead info and conversation history
    - Allows user to continue without re-submitting lead form
    """
    try:
        session_data = await rag.restore_session(request.sessionId)
        
        if not session_data:
            return SessionRestoreResponse(
                success=False,
                message="Session not found or expired. Please submit the lead form again."
            )
        
        conversation = session_data.get('conversation', {})
        
        return SessionRestoreResponse(
            success=True,
            sessionId=request.sessionId,
            lead=session_data['lead'],
            messages=session_data.get('messages', []),
            isEscalated=conversation.get('isEscalated', False) if conversation else False,
            message="Session restored successfully. Welcome back!"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Session restoration error: {str(e)}"
        )


@router.post("/session/check", response_model=SessionCheckResponse)
async def check_session(
    request: SessionCheckRequest,
    postgresql: PostgreSQLService = Depends(get_postgresql_service)
) -> SessionCheckResponse:
    """
    Check if a session is valid and get basic info.
    
    Used by frontend to check localStorage session on app load.
    """
    try:
        is_valid = await postgresql.check_session_valid(request.sessionId)
        
        if not is_valid:
            return SessionCheckResponse(
                valid=False,
                sessionId=request.sessionId
            )
        
        lead = await postgresql.get_lead_by_session(request.sessionId)
        
        if not lead:
            return SessionCheckResponse(
                valid=False,
                sessionId=request.sessionId
            )
        
        # Calculate expiration (24 hours from creation)
        created_at = lead.get('createdAt')
        expires_at = None
        if created_at:
            from datetime import datetime, timedelta
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            expires_at = (created_at + timedelta(hours=24)).isoformat()
        
        return SessionCheckResponse(
            valid=True,
            sessionId=request.sessionId,
            lead=lead,
            expiresAt=expires_at
        )
        
    except Exception as e:
        return SessionCheckResponse(
            valid=False,
            sessionId=request.sessionId
        )


@router.get("/conversation/{session_id}")
async def get_conversation(
    session_id: str,
    postgresql: PostgreSQLService = Depends(get_postgresql_service)
):
    """Get conversation history by session ID."""
    summary = await postgresql.get_lead_conversation_summary(session_id)
    
    if not summary.get('lead'):
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return summary
