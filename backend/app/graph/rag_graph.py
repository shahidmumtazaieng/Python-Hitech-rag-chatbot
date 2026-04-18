"""LangGraph RAG Pipeline for Hitech Chatbot."""
from typing import List, Dict, Any, TypedDict, Optional

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

from app.config import get_settings
from app.services.pinecone_service import get_pinecone_service


class RAGState(TypedDict):
    """State for the RAG pipeline."""
    question: str
    generation: str
    documents: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]          # ← was missing — caused silent drop
    conversation_history: List[Dict[str, str]]
    session_id: str
    lead_info: Dict[str, Any]
    retries: int


class RAGPipeline:
    """LangGraph RAG Pipeline."""

    def __init__(self):
        self.settings = get_settings()
        # Use Groq with Llama 3.1 8B (fast and free tier available)
        self.llm = ChatGroq(
            model=self.settings.GROQ_MODEL,
            temperature=self.settings.GROQ_TEMPERATURE,
            max_tokens=self.settings.GROQ_MAX_TOKENS,
            groq_api_key=self.settings.GROQ_API_KEY,
        )
        self.pinecone = get_pinecone_service()
        self.graph = self._build_graph()

    # ------------------------------------------------------------------
    # Graph wiring
    # ------------------------------------------------------------------

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(RAGState)
        workflow.add_node("retrieve", self._retrieve_documents)
        workflow.add_node("grade_documents", self._grade_documents)
        workflow.add_node("generate", self._generate_response)
        workflow.add_node("transform_query", self._transform_query)

        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_conditional_edges(
            "grade_documents",
            self._decide_to_generate,
            {"transform_query": "transform_query", "generate": "generate"},
        )
        workflow.add_edge("transform_query", "retrieve")
        workflow.add_edge("generate", END)
        return workflow.compile()

    # ------------------------------------------------------------------
    # Nodes
    # ------------------------------------------------------------------

    def _retrieve_documents(self, state: RAGState) -> RAGState:
        print(f"[RAG] Retrieving for: {state['question'][:80]}")
        try:
            docs = self.pinecone.similarity_search(
                query=state['question'],
                top_k=self.settings.RAG_TOP_K,
            )
            filtered = [d for d in docs if d.get('score', 0) >= self.settings.RAG_SIMILARITY_THRESHOLD]
            print(f"[RAG] {len(filtered)} docs above threshold {self.settings.RAG_SIMILARITY_THRESHOLD}")
        except Exception as exc:
            print(f"[RAG] Retrieval error: {exc}")
            filtered = []
        return {**state, "documents": filtered}

    def _grade_documents(self, state: RAGState) -> RAGState:
        # Already filtered by threshold; keep as-is
        return state

    def _decide_to_generate(self, state: RAGState) -> str:
        if state['retries'] >= 2 or state['documents']:
            return "generate"
        return "transform_query"

    def _transform_query(self, state: RAGState) -> RAGState:
        print(f"[RAG] Transforming query (retry {state.get('retries', 0) + 1})")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Rewrite the question with different keywords to improve retrieval. Return only the rewritten question, nothing else."),
            ("human", "Original: {question}"),
        ])
        try:
            result = (prompt | self.llm).invoke({"question": state['question']})
            new_q = result.content.strip().split('\n')[0].lstrip('123.-* ')
        except Exception:
            new_q = state['question']
        return {**state, "question": new_q, "retries": state.get('retries', 0) + 1}

    def _generate_response(self, state: RAGState) -> RAGState:
        # Build context + sources
        context_parts, sources = [], []
        for i, doc in enumerate(state['documents'][:3], 1):
            context_parts.append(f"[Document {i}]\n{doc['content']}")
            sources.append({
                'title': doc.get('title', ''),
                'url': doc.get('url', ''),
                'source': doc.get('source', ''),
                'score': doc.get('score', 0),
            })

        context = "\n\n".join(context_parts) if context_parts else "No relevant documents found in knowledge base."

        # Conversation history
        history_msgs = []
        for msg in state.get('conversation_history', []):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'user':
                history_msgs.append(HumanMessage(content=content))
            elif role == 'assistant':
                history_msgs.append(AIMessage(content=content))

        lead = state.get('lead_info', {})
        lead_name = lead.get('fullName', lead.get('full_name', 'Customer'))
        inquiry = lead.get('inquiryType', lead.get('inquiry_type', 'General Inquiry'))

        system_prompt = f"""You are Hitech Assistant, an AI-powered customer service representative for Hitech Steel Industries — a leading steel manufacturer in Saudi Arabia.

CUSTOMER: {lead_name} | Inquiry: {inquiry}

INSTRUCTIONS:
1. Answer ONLY from the context documents below.
2. If the answer isn't in the context, say: "I don't have specific information about that. Let me connect you with a human representative who can help."
3. Be professional, concise, and friendly.
4. For pricing, provide ranges if available, otherwise suggest speaking with sales.
5. Support both English and Arabic naturally.

CONTEXT:
{context}"""

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="history"),
            HumanMessage(content=state['question']),
        ])

        try:
            print(f"[RAG] Generating response with Groq (model: {self.settings.GROQ_MODEL})")
            result = (prompt | self.llm).invoke({"history": history_msgs})
            generation = result.content
            print(f"[RAG] Response generated successfully ({len(generation)} chars)")
        except Exception as exc:
            print(f"[RAG] Generation error: {exc}")
            import traceback
            traceback.print_exc()
            generation = f"I apologize, I'm having trouble generating a response. Error: {str(exc)}"

        return {**state, "generation": generation, "sources": sources}

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def invoke(
        self,
        question: str,
        conversation_history: List[Dict],
        session_id: str,
        lead_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        initial: RAGState = {
            "question": question,
            "generation": "",
            "documents": [],
            "sources": [],
            "conversation_history": conversation_history,
            "session_id": session_id,
            "lead_info": lead_info,
            "retries": 0,
        }
        
        try:
            result = self.graph.invoke(initial)
            
            # Ensure generation key exists
            if "generation" not in result:
                print(f"[RAG] Warning: 'generation' key missing in result. Keys: {result.keys()}")
                result["generation"] = "I apologize, but I couldn't generate a response. Please try again."
            
            return {
                "response": result.get("generation", "No response generated"),
                "sources": result.get("sources", []),
                "documents_used": len(result.get("documents", [])),
            }
        except Exception as e:
            print(f"[RAG] Error during invocation: {e}")
            import traceback
            traceback.print_exc()
            return {
                "response": f"Error: {str(e)}",
                "sources": [],
                "documents_used": 0,
            }


# Singleton
_rag_pipeline: Optional[RAGPipeline] = None


def create_rag_graph() -> RAGPipeline:
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline