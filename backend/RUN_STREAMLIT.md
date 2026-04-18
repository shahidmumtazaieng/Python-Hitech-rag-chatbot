# ============================================
# Groq + Streamlit RAG Test - Quick Start
# ============================================

## 1. Install Dependencies
pip install langchain-groq groq streamlit

## 2. Verify Installation
python -c "from groq import Groq; print('✅ Groq installed')"
python -c "from langchain_groq import ChatGroq; print('✅ LangChain-Groq installed')"

## 3. Run Streamlit App
python -m streamlit run streamlit_rag_test.py

## 4. Open in Browser
# The app will open automatically at: http://localhost:8501

## 5. Test the RAG Pipeline
- Click any "Quick Test" button (Q1-Q5)
- Or type your own question
- Watch Groq (Llama 3.1) generate responses with retrieved documents

## Current Configuration:
- LLM: Groq (llama-3.1-8b-instant)
- Vector Store: Pinecone (15 vectors, 1024-dim)
- Embeddings: Hugging Face API (BGE-M3)
- Database: PostgreSQL (Neon)

## API Keys Status:
✅ GROQ_API_KEY: Configured
✅ PINECONE_API_KEY: Configured  
✅ HF_API_TOKEN: Configured
✅ DATABASE_URL: Configured
