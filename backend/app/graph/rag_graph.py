"""LangGraph RAG Pipeline for Hitech Chatbot."""
from typing import List, Dict, Any, TypedDict, Annotated
from operator import add
import json

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from app.config import get_settings
from app.services.pinecone_service import get_pinecone_service


class RAGState(TypedDict):
    """State for the RAG pipeline."""
    question: str
    generation: str
    documents: List[Dict[str, Any]]
    conversation_history: List[Dict[str, str]]
    session_id: str
    lead_info: Dict[str, Any]
    retries: int


class RAGPipeline:
    """LangGraph RAG Pipeline implementation."""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = ChatGoogleGenerativeAI(
            model=self.settings.GEMINI_MODEL,
            temperature=self.settings.GEMINI_TEMPERATURE,
            max_output_tokens=self.settings.GEMINI_MAX_TOKENS,
            google_api_key=self.settings.GEMINI_API_KEY
        )
        self.pinecone = get_pinecone_service()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(RAGState)
        
        # Add nodes
        workflow.add_node("retrieve", self._retrieve_documents)
        workflow.add_node("grade_documents", self._grade_documents)
        workflow.add_node("generate", self._generate_response)
        workflow.add_node("transform_query", self._transform_query)
        
        # Set entry point
        workflow.set_entry_point("retrieve")
        
        # Add edges
        workflow.add_edge("retrieve", "grade_documents")
        
        # Conditional edge from grade_documents
        workflow.add_conditional_edges(
            "grade_documents",
            self._decide_to_generate,
            {
                "transform_query": "transform_query",
                "generate": "generate"
            }
        )
        
        workflow.add_edge("transform_query", "retrieve")
        workflow.add_edge("generate", END)
        
        return workflow.compile()
    
    def _retrieve_documents(self, state: RAGState) -> RAGState:
        """Retrieve documents from vector store."""
        print(f"Retrieving documents for: {state['question']}")
        
        documents = self.pinecone.similarity_search(
            query=state['question'],
            top_k=self.settings.RAG_TOP_K
        )
        
        # Filter by similarity threshold
        filtered_docs = [
            doc for doc in documents 
            if doc.get('score', 0) >= self.settings.RAG_SIMILARITY_THRESHOLD
        ]
        
        print(f"Retrieved {len(filtered_docs)} relevant documents")
        
        return {
            **state,
            "documents": filtered_docs
        }
    
    def _grade_documents(self, state: RAGState) -> RAGState:
        """Grade retrieved documents for relevance."""
        if not state['documents']:
            return {**state, "documents": []}
        
        # Simple grading based on similarity score
        # Documents already filtered by threshold in retrieval
        graded_docs = []
        for doc in state['documents']:
            if doc.get('score', 0) >= self.settings.RAG_SIMILARITY_THRESHOLD:
                graded_docs.append(doc)
        
        return {
            **state,
            "documents": graded_docs
        }
    
    def _decide_to_generate(self, state: RAGState) -> str:
        """Decide whether to generate or transform query."""
        if state['retries'] >= 2:
            # Max retries reached, generate anyway
            return "generate"
        
        if not state['documents']:
            # No relevant documents, transform query
            return "transform_query"
        
        return "generate"
    
    def _transform_query(self, state: RAGState) -> RAGState:
        """Transform query for better retrieval."""
        print(f"Transforming query: {state['question']}")
        
        transform_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at reformulating questions for better search results.
            Given the original question, create 3 alternative versions that might retrieve better results.
            Focus on using different keywords and phrasings while maintaining the original intent.
            Return only the reformulated questions, one per line."""),
            ("human", "Original question: {question}")
        ])
        
        chain = transform_prompt | self.llm
        result = chain.invoke({"question": state['question']})
        
        # Use the first reformulation as the new query
        new_question = result.content.strip().split('\n')[0]
        if new_question.startswith(('1.', '2.', '3.', '-', '*')):
            new_question = new_question[2:].strip()
        
        print(f"Transformed to: {new_question}")
        
        return {
            **state,
            "question": new_question,
            "retries": state.get('retries', 0) + 1
        }
    
    def _generate_response(self, state: RAGState) -> RAGState:
        """Generate response using retrieved documents."""
        # Build context from documents
        context_parts = []
        sources = []
        
        for i, doc in enumerate(state['documents'][:3], 1):  # Top 3 docs
            context_parts.append(f"[Document {i}]\n{doc['content']}")
            sources.append({
                'title': doc.get('title', ''),
                'url': doc.get('url', ''),
                'source': doc.get('source', '')
            })
        
        context = "\n\n".join(context_parts) if context_parts else "No relevant documents found."
        
        # Build conversation history
        history_messages = []
        for msg in state.get('conversation_history', []):
            if msg.get('role') == 'user':
                history_messages.append(HumanMessage(content=msg['content']))
            else:
                history_messages.append(AIMessage(content=msg['content']))
        
        # Lead info for personalization
        lead_info = state.get('lead_info', {})
        lead_name = lead_info.get('fullName', 'Customer')
        inquiry_type = lead_info.get('inquiryType', 'General Inquiry')
        
        # System prompt
        system_prompt = f"""You are Hitech Assistant, an AI-powered customer service representative for Hitech Steel Industries.

COMPANY CONTEXT:
Hitech Steel Industries is a leading steel manufacturer in Saudi Arabia, providing high-quality steel products and services for construction, infrastructure, and industrial projects.

CUSTOMER INFORMATION:
- Name: {lead_name}
- Inquiry Type: {inquiry_type}

INSTRUCTIONS:
1. Answer questions based ONLY on the provided context documents
2. If the answer is not in the context, say: "I don't have specific information about that in my knowledge base. Let me connect you with a human representative who can help."
3. Be professional, friendly, and concise
4. Use Arabic greetings if the customer writes in Arabic
5. For pricing questions, provide general ranges if available, otherwise suggest speaking with sales
6. Always offer to escalate to a human if the question is complex or requires detailed technical specifications

CONVERSATION HISTORY:
Use the conversation history to maintain context and provide coherent responses.

CONTEXT DOCUMENTS:
{context}
"""
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="history"),
            HumanMessage(content=state['question'])
        ])
        
        # Generate response
        chain = prompt | self.llm
        result = chain.invoke({"history": history_messages})
        
        return {
            **state,
            "generation": result.content,
            "sources": sources
        }
    
    def invoke(self, question: str, conversation_history: List[Dict], 
               session_id: str, lead_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the RAG pipeline.
        
        Args:
            question: User question
            conversation_history: List of previous messages
            session_id: Session identifier
            lead_info: Lead information
            
        Returns:
            Dictionary with generation and sources
        """
        initial_state = RAGState(
            question=question,
            generation="",
            documents=[],
            conversation_history=conversation_history,
            session_id=session_id,
            lead_info=lead_info,
            retries=0
        )
        
        result = self.graph.invoke(initial_state)
        
        return {
            "response": result['generation'],
            "sources": result.get('sources', []),
            "documents_used": len(result.get('documents', []))
        }


# Global instance
_rag_pipeline = None


def create_rag_graph() -> RAGPipeline:
    """Create or get RAG pipeline instance."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
