"""Chat router for message handling."""
from fastapi import APIRouter, HTTPException, Depends

from app.models.chat import ChatRequest, ChatResponse, TalkToHumanRequest, TalkToHumanResponse
from app.models.conversation import MessageRole
from app.services.mongodb_service import MongoDBService, get_mongodb_service
from app.services.rag_service import RAGService, get_rag_service

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat/sync", response_model=ChatResponse)
async def chat_sync(
    request: ChatRequest,
    mongodb: MongoDBService = Depends(get_mongodb_service),
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
        lead = await mongodb.get_lead_by_session(request.sessionId)
        if not lead:
            raise HTTPException(
                status_code=404,
                detail="Session not found. Please submit lead form first."
            )
        
        # Check if conversation is escalated
        conversation = await mongodb.get_conversation(request.sessionId)
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
    mongodb: MongoDBService = Depends(get_mongodb_service),
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
        lead = await mongodb.get_lead_by_session(request.sessionId)
        if not lead:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        # Get conversation summary for notes
        summary = await rag.get_conversation_summary(request.sessionId)
        full_notes = f"{request.notes or ''}\n\n{summary}".strip()
        
        # Escalate conversation
        success = await mongodb.escalate_to_human(
            request.sessionId,
            notes=full_notes
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to escalate conversation"
            )
        
        # Add system message about escalation
        await mongodb.add_message(
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


@router.get("/conversation/{session_id}")
async def get_conversation(
    session_id: str,
    mongodb: MongoDBService = Depends(get_mongodb_service)
):
    """Get conversation history by session ID."""
    conversation = await mongodb.get_conversation(session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation
