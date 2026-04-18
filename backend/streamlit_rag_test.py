#!/usr/bin/env python3
"""
Streamlit RAG Testing App for Hitech Chatbot
Tests the RAG pipeline with Groq (Llama 3.1), Pinecone, and BGE-M3 embeddings
"""

import streamlit as st
import sys
import os
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
load_dotenv()
# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page config
st.set_page_config(
    page_title="Hitech RAG Test",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #E30613;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #f0f2f6;
        border-left: 4px solid #003087;
    }
    .assistant-message {
        background-color: #fff5f5;
        border-left: 4px solid #E30613;
    }
    .source-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.3rem;
        padding: 0.5rem;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
    }
    .stButton>button {
        background-color: #E30613;
        color: white;
        border-radius: 0.3rem;
    }
    .stButton>button:hover {
        background-color: #C00510;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'rag_pipeline' not in st.session_state:
    st.session_state.rag_pipeline = None
if 'services_initialized' not in st.session_state:
    st.session_state.services_initialized = False
if 'lead_info' not in st.session_state:
    st.session_state.lead_info = {
        "fullName": "Test User",
        "email": "test@example.com",
        "inquiryType": "Product Information"
    }

@st.cache_resource
def initialize_services():
    """Initialize RAG services (cached for performance)."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import services
        from app.config import get_settings
        from app.services.pinecone_service import pinecone_service
        from app.services.embedding_service import embedding_service
        from app.services.hf_embedding_service import get_hf_embedding_service
        from app.graph.rag_graph import create_rag_graph
        
        settings = get_settings()
        
        # Initialize Pinecone
        try:
            pinecone_service.initialize()
            pinecone_status = "✅ Connected"
        except Exception as e:
            pinecone_status = f"❌ Error: {str(e)[:50]}"
        
        # Load local embedding model (fallback)
        _ = embedding_service
        local_embedding_status = "✅ Loaded"
        
        # Initialize HF Embedding Service (for fast query embeddings)
        try:
            hf_service = get_hf_embedding_service()
            hf_status = hf_service.get_status()
            if hf_status['api_configured']:
                hf_embedding_status = "✅ HF API Ready"
            else:
                hf_embedding_status = "⚠️ HF API Key Missing (using local fallback)"
        except Exception as e:
            hf_embedding_status = f"⚠️ HF Error: {str(e)[:50]}"
        
        # Create RAG pipeline
        rag_graph = create_rag_graph()
        rag_status = "✅ Ready"
        
        return {
            "settings": settings,
            "pinecone_service": pinecone_service,
            "embedding_service": embedding_service,
            "hf_service": hf_service if 'hf_service' in locals() else None,
            "rag_graph": rag_graph,
            "pinecone_status": pinecone_status,
            "local_embedding_status": local_embedding_status,
            "hf_embedding_status": hf_embedding_status,
            "rag_status": rag_status,
            "initialized": True
        }
    except Exception as e:
        st.error(f"Failed to initialize services: {e}")
        return {
            "initialized": False,
            "error": str(e)
        }

def render_header():
    """Render app header."""
    st.markdown('<div class="main-header">🤖 Hitech RAG Test</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Test your RAG pipeline with Groq (Llama 3.1), Pinecone & BGE-M3</div>', unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar with configuration."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Services status
        st.subheader("Services Status")
        if st.session_state.services_initialized:
            services = st.session_state.services
            st.success(f"Pinecone: {services['pinecone_status']}")
            st.success(f"Local Embeddings: {services['local_embedding_status']}")
            st.info(f"HF API (Query): {services['hf_embedding_status']}")
            st.success(f"RAG Pipeline: {services['rag_status']}")
            
            # Show embedding strategy
            st.divider()
            st.caption("📊 Embedding Strategy")
            st.markdown("""
            - **Ingestion**: Local all-MiniLM-L6-v2 (384-dim)
            - **Query**: HF API BGE-M3 (1024-dim) → Fallback to local
            """)
        else:
            st.warning("Services not initialized")
        
        # Lead info
        st.subheader("👤 Test Lead Info")
        st.session_state.lead_info["fullName"] = st.text_input("Name", st.session_state.lead_info["fullName"])
        st.session_state.lead_info["email"] = st.text_input("Email", st.session_state.lead_info["email"])
        st.session_state.lead_info["inquiryType"] = st.selectbox(
            "Inquiry Type",
            ["Product Information", "Pricing Quote", "Technical Support", "Partnership", "Careers", "Other"],
            index=0
        )
        
        # RAG Settings
        st.subheader("🔧 RAG Settings")
        if st.session_state.services_initialized:
            settings = st.session_state.services["settings"]
            st.text(f"Model: {settings.GROQ_MODEL} (via Groq)")
            st.text(f"Top-K: {settings.RAG_TOP_K}")
            st.text(f"Threshold: {settings.RAG_SIMILARITY_THRESHOLD}")
        
        # Actions
        st.subheader("🛠️ Actions")
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()
        
        if st.button("📊 Test Vector Store"):
            test_vector_store()
        
        # Stats
        if st.session_state.messages:
            st.subheader("📈 Session Stats")
            st.text(f"Messages: {len(st.session_state.messages)}")
            user_msgs = len([m for m in st.session_state.messages if m['role'] == 'user'])
            st.text(f"User: {user_msgs}")
            st.text(f"Assistant: {len(st.session_state.messages) - user_msgs}")

def test_vector_store():
    """Test vector store connection and stats."""
    try:
        services = st.session_state.services
        pinecone = services["pinecone_service"]
        
        if hasattr(pinecone, 'index') and pinecone.index:
            stats = pinecone.get_stats()
            st.sidebar.success(f"📊 Vectors: {stats.get('total_vectors', 'N/A')}")
            st.sidebar.text(f"Dimension: {stats.get('dimension', 'N/A')}")
        else:
            st.sidebar.error("Pinecone not initialized")
    except Exception as e:
        st.sidebar.error(f"Error: {str(e)[:100]}")

def process_message(user_input: str) -> Dict[str, Any]:
    """Process user message through RAG pipeline."""
    try:
        services = st.session_state.services
        rag_graph = services["rag_graph"]
        
        # Generate session ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # Run RAG pipeline
        result = rag_graph.invoke(
            question=user_input,
            conversation_history=st.session_state.conversation_history,
            session_id=session_id,
            lead_info=st.session_state.lead_info
        )
        
        # Update conversation history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": result['generation']
        })
        
        # Keep only last 10 messages for context
        st.session_state.conversation_history = st.session_state.conversation_history[-10:]
        
        return {
            "response": result['generation'],
            "sources": result.get('sources', []),
            "documents_used": result.get('documents_used', 0),
            "success": True
        }
    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "sources": [],
            "documents_used": 0,
            "success": False,
            "error": str(e)
        }

def render_chat():
    """Render chat interface."""
    st.subheader("💬 Chat Test")
    
    # Display messages
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            st.markdown(f'''
                <div class="chat-message user-message">
                    <strong>👤 You:</strong><br>{msg['content']}
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
                <div class="chat-message assistant-message">
                    <strong>🤖 Assistant:</strong><br>{msg['content']}
                </div>
            ''', unsafe_allow_html=True)
            
            # Show sources if available
            if msg.get('sources'):
                with st.expander(f"📚 Sources ({len(msg['sources'])} documents)"):
                    for i, src in enumerate(msg['sources'], 1):
                        st.markdown(f'''
                            <div class="source-box">
                                <strong>Source {i}</strong> 
                                (Score: {src.get('score', 'N/A'):.3f})<br>
                                <em>{src.get('title', 'Untitled')}</em><br>
                                {src.get('content', '')[:300]}...
                            </div>
                        ''', unsafe_allow_html=True)

def render_input():
    """Render input area."""
    with st.container():
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.text_input(
                "Type your message...",
                key="user_input",
                placeholder="Ask about Hitech Steel products, services, or any question...",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.button("Send 📤", use_container_width=True)
        
        if send_button and user_input.strip():
            if not st.session_state.services_initialized:
                st.error("❌ Services not initialized. Please check your configuration.")
                return
            
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # Process with RAG
            with st.spinner("🤔 Thinking... (RAG pipeline processing)"):
                result = process_message(user_input)
            
            # Add assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": result['response'],
                "sources": result.get('sources', []),
                "documents_used": result.get('documents_used', 0),
                "timestamp": datetime.now().isoformat()
            })
            
            # Clear input and rerun
            st.rerun()

def render_quick_tests():
    """Render quick test buttons."""
    st.subheader("🧪 Quick Tests")
    
    test_questions = [
        "What steel products does Hitech offer?",
        "Tell me about your pricing",
        "How can I contact sales?",
        "What are your delivery options?",
        "Do you offer custom steel fabrication?"
    ]
    
    cols = st.columns(len(test_questions))
    for i, question in enumerate(test_questions):
        with cols[i]:
            if st.button(f"Q{i+1}", help=question):
                if not st.session_state.services_initialized:
                    st.error("Services not initialized")
                    return
                
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": question,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Process with RAG
                with st.spinner("Processing..."):
                    result = process_message(question)
                
                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result['response'],
                    "sources": result.get('sources', []),
                    "documents_used": result.get('documents_used', 0),
                    "timestamp": datetime.now().isoformat()
                })
                
                st.rerun()

def main():
    """Main app function."""
    render_header()
    
    # Initialize services
    if not st.session_state.services_initialized:
        with st.spinner("🚀 Initializing RAG services..."):
            services = initialize_services()
            if services.get("initialized"):
                st.session_state.services = services
                st.session_state.services_initialized = True
                st.success("✅ Services initialized successfully!")
            else:
                st.error(f"❌ Failed to initialize: {services.get('error', 'Unknown error')}")
                st.info("💡 Make sure your .env file has the correct API keys")
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    if st.session_state.services_initialized:
        render_quick_tests()
        render_chat()
        render_input()
    else:
        st.warning("⚠️ Please fix the initialization errors above to start testing.")
        
        # Show troubleshooting
        with st.expander("🔧 Troubleshooting"):
            st.markdown("""
            ### Common Issues:
            
            1. **Missing API Keys**: Ensure your `.env` file has:
               - `GROQ_API_KEY` (from https://console.groq.com/keys)
               - `PINECONE_API_KEY`
               - `HF_API_TOKEN` (from https://huggingface.co/settings/tokens)
               - `DATABASE_URL` (for session persistence)
            
            2. **Pinecone Index**: Make sure your Pinecone index exists and has vectors
            
            3. **Python Path**: Run from the backend directory:
               ```bash
               cd backend
               pip install langchain-groq groq
               streamlit run streamlit_rag_test.py
               ```
            """)

if __name__ == "__main__":
    main()
