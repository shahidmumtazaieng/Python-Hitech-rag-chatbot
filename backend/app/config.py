"""Configuration settings for the Hitech RAG Chatbot backend."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Hitech RAG Chatbot"
    DEBUG: bool = False
    BACKEND_URL: str = "http://localhost:8000"

    # PostgreSQL (Neon)
    DATABASE_URL: str = "postgresql://neondb_owner:npg_3Fo4mQwPeHvE@ep-empty-queen-an57qg84-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

    # MongoDB (legacy — kept for potential future use)
    MONGODB_URI: str = "mongodb://localhost:27017/hitech-chatbot"
    MONGODB_DB_NAME: str = "hitech-chatbot"

    # Pinecone
    PINECONE_API_KEY: str = "pcsk_7QHnqA_JEyjLY8ESJucuUYUTqQkTMAquMDKYoSsemJijBKNq5UpbgtdJ6jmE16x4u7Cefh"
    PINECONE_ENVIRONMENT: str = "gcp-starter"
    PINECONE_HOST: Optional[str] = "https://hitech-nsl1vdk.svc.aped-4627-b74a.pinecone.io"
    PINECONE_INDEX_NAME: str = "hitech-kb-index"
    PINECONE_DIMENSION: int = 384  # Must match embedding model output (all-MiniLM-L6-v2)

    # Google Gemini (kept for future use)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_TEMPERATURE: float = 0.3
    GEMINI_MAX_TOKENS: int = 2048
    
    # Groq (Primary LLM - Fast inference)
    GROQ_API_KEY: str = "your-groq-api-key"
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_TEMPERATURE: float = 0.3
    GROQ_MAX_TOKENS: int = 2048

    # Conversation
    MAX_CONVERSATION_HISTORY: int = 10

    # RAG Configuration
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.3   # ← lowered from 0.7 for better recall
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # Session
    SESSION_TTL_HOURS: int = 24

    # Scraping
    SCRAPE_BASE_URL: str = "https://www.hitech.sa"
    SCRAPE_MAX_PAGES: int = 100
    SCRAPE_DELAY: float = 1.0

    # CORS
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

    @property
    def cors_origins_list(self) -> list:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()