"""Configuration settings for the Hitech RAG Chatbot backend."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Hitech RAG Chatbot"
    DEBUG: bool = False
    BACKEND_URL: str = "http://localhost:8000"
    
    # PostgreSQL (Neon)
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/hitech_chatbot"
    
    # MongoDB (keeping for potential future use)
    MONGODB_URI: str = "mongodb://localhost:27017/hitech-chatbot"
    MONGODB_DB_NAME: str = "hitech-chatbot"
    
    # Pinecone
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "gcp-starter"
    PINECONE_HOST: Optional[str] = None
    PINECONE_INDEX_NAME: str = "hitech-kb-index"
    PINECONE_DIMENSION: int = 384  # Embedding dimension (all-MiniLM-L6-v2)
    
    # Google Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash-preview-05-20"
    GEMINI_TEMPERATURE: float = 0.3
    GEMINI_MAX_TOKENS: int = 2048
    
    # Conversation settings
    MAX_CONVERSATION_HISTORY: int = 10
    
    # RAG Configuration
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # Session
    SESSION_TTL_HOURS: int = 24
    MAX_CONVERSATION_HISTORY: int = 10
    
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
        # Prioritize .env file over system environment
        env_prefix = ""
        env_nested_delimiter = "__"
    
    @property
    def cors_origins_list(self) -> list:
        """Parse CORS origins from string."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
