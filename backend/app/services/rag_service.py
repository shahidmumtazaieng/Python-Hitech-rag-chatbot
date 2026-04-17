"""RAG Service - Main service for chat responses."""
from typing import List, Dict, Any, Optional

from app.config import get_settings
from app.models.chat import ChatRequest, ChatResponse, SourceDocument
from app.models.conversation import MessageRole
from app.services.mongodb_service import get_mongodb_service
from app.graph.rag_graph import create_rag_graph


class RAGService:
    """Service for handling RAG-based chat responses."""
    
    def __init__(self):
        self.settings = get_settings()
        self.mongodb = get_mongodb_service()
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
        # Get conversation history for context
        conversation_history = await self.mongodb.get_conversation_history(
            request.sessionId,
            limit=self.settings.MAX_CONVERSATION_HISTORY
        )
        
        # Format history for LangGraph
        history_for_graph = [
            {"role": msg.role.value, "content": msg.content}
            for msg in conversation_history
        ]
        
        # Run RAG pipeline
        result = self.rag_graph.invoke(
            question=request.message,
            conversation_history=history_for_graph,
            session_id=request.sessionId,
            lead_info=lead_info
        )
        
        # Store user message
        await self.mongodb.add_message(
            session_id=request.sessionId,
            role=MessageRole.USER,
            content=request.message
        )
        
        # Store assistant response
        await self.mongodb.add_message(
            session_id=request.sessionId,
            role=MessageRole.ASSISTANT,
            content=result['response'],
            metadata={
                "sources": result.get('sources', []),
                "documents_used": result.get('documents_used', 0),
                "model": self.settings.GEMINI_MODEL
            }
        )
        
        # Format sources
        sources = None
        if result.get('sources'):
            sources = [
                SourceDocument(
                    content=src.get('content', ''),
                    source=src.get('source', ''),
                    title=src.get('title'),
                    score=src.get('score')
                )
                for src in result['sources']
            ]
        
        return ChatResponse(
            response=result['response'],
            sessionId=request.sessionId,
            sources=sources,
            model=self.settings.GEMINI_MODEL
        )
    
    async def get_conversation_summary(self, session_id: str) -> str:
        """Get a summary of the conversation for human handoff."""
        conversation = await self.mongodb.get_conversation(session_id)
        if not conversation:
            return "No conversation found."
        
        messages = conversation.get('messages', [])
        if not messages:
            return "Empty conversation."
        
        # Build summary
        summary_parts = ["Conversation Summary:"]
        for msg in messages[-10:]:  # Last 10 messages
            role = "User" if msg['role'] == 'user' else "Assistant"
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            summary_parts.append(f"{role}: {content}")
        
        return "\n".join(summary_parts)


# Global instance
rag_service = RAGService()


def get_rag_service() -> RAGService:
    """Get the RAG service instance."""
    return rag_service
