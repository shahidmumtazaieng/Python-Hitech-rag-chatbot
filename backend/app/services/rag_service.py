"""RAG Service - Main service for chat responses."""
from typing import List, Dict, Any, Optional

from app.config import get_settings
from app.models.chat import ChatRequest, ChatResponse, SourceDocument
from app.models.conversation import MessageRole
from app.services.postgresql_service import get_postgresql_service
from app.graph.rag_graph import create_rag_graph


class RAGService:
    """Service for handling RAG-based chat responses."""
    
    def __init__(self):
        self.settings = get_settings()
        self.postgresql = get_postgresql_service()
        self.rag_graph = create_rag_graph()
    
    async def process_chat(self, request: ChatRequest, lead_info: Dict[str, Any]) -> ChatResponse:
        """
        Process a chat message and generate RAG-based response.
        
        Args:
            request: Chat request with message and session ID
            lead_info: Lead information for personalization
            
        Returns:
            ChatResponse with generated response
        """
        # Ensure conversation exists
        await self.postgresql.get_or_create_conversation(request.sessionId)
        
        # Get conversation history for context
        conversation_history = await self.postgresql.get_conversation_history(
            request.sessionId,
            limit=self.settings.MAX_CONVERSATION_HISTORY
        )
        
        # Format history for LangGraph (handle both dict and object formats)
        history_for_graph = []
        for msg in conversation_history:
            if isinstance(msg, dict):
                role = msg.get('role', 'user')
                content = msg.get('content', '')
            else:
                role = msg.role.value if hasattr(msg, 'role') else msg.get('role', 'user')
                content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
            history_for_graph.append({"role": role, "content": content})
        
        # Run RAG pipeline
        result = self.rag_graph.invoke(
            question=request.message,
            conversation_history=history_for_graph,
            session_id=request.sessionId,
            lead_info=lead_info
        )
        
        # Store user message
        await self.postgresql.add_message(
            session_id=request.sessionId,
            role=MessageRole.USER,
            content=request.message
        )
        
        # Store assistant response with sources
        sources_data = result.get('sources', [])
        await self.postgresql.add_message(
            session_id=request.sessionId,
            role=MessageRole.ASSISTANT,
            content=result['response'],
            sources=sources_data if sources_data else None,
            metadata={
                "documents_used": result.get('documents_used', 0),
                "model": self.settings.GEMINI_MODEL
            }
        )
        
        # Format sources for response
        sources = None
        if sources_data:
            sources = [
                SourceDocument(
                    content=src.get('content', ''),
                    source=src.get('source', ''),
                    title=src.get('title'),
                    score=src.get('score')
                )
                for src in sources_data
            ]
        
        return ChatResponse(
            response=result['response'],
            sessionId=request.sessionId,
            sources=sources,
            model=self.settings.GEMINI_MODEL
        )
    
    async def get_conversation_summary(self, session_id: str) -> str:
        """Get a summary of the conversation for human handoff."""
        summary_data = await self.postgresql.get_lead_conversation_summary(session_id)
        
        lead = summary_data.get('lead')
        messages = summary_data.get('messages', [])
        
        if not lead:
            return "No lead or conversation found."
        
        if not messages:
            return f"Lead: {lead.get('fullName', 'Unknown')} - No messages yet."
        
        # Build summary
        summary_parts = [
            "=" * 50,
            "CONVERSATION SUMMARY FOR HUMAN AGENT",
            "=" * 50,
            f"Lead: {lead.get('fullName', 'Unknown')}",
            f"Email: {lead.get('email', 'N/A')}",
            f"Phone: {lead.get('phone', 'N/A')}",
            f"Company: {lead.get('company', 'N/A')}",
            f"Inquiry Type: {lead.get('inquiryType', 'N/A')}",
            "-" * 50,
            "RECENT MESSAGES:",
            "-" * 50
        ]
        
        for msg in messages[-10:]:  # Last 10 messages
            role = "User" if msg.get('role') == 'user' else "Assistant"
            content = msg.get('content', '')
            # Truncate long messages
            if len(content) > 150:
                content = content[:150] + "..."
            summary_parts.append(f"{role}: {content}")
        
        summary_parts.extend([
            "-" * 50,
            f"Total Messages: {len(messages)}",
            "=" * 50
        ])
        
        return "\n".join(summary_parts)
    
    async def restore_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Restore a session by ID - checks validity and returns lead info."""
        is_valid = await self.postgresql.check_session_valid(session_id)
        if not is_valid:
            return None
        
        summary = await self.postgresql.get_lead_conversation_summary(session_id)
        if not summary.get('lead'):
            return None
        
        return {
            "sessionId": session_id,
            "lead": summary['lead'],
            "conversation": summary['conversation'],
            "messages": summary['messages'],
            "isValid": True
        }


# Global instance
rag_service = RAGService()


def get_rag_service() -> RAGService:
    """Get the RAG service instance."""
    return rag_service
