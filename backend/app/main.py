"""Main FastAPI application for Hitech RAG Chatbot."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.services.mongodb_service import mongodb_service
from app.services.pinecone_service import pinecone_service
from app.services.embedding_service import embedding_service
from app.routers import lead_router, chat_router, ingest_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    settings = get_settings()
    print(f"Starting {settings.APP_NAME}...")
    
    # Connect to MongoDB
    await mongodb_service.connect()
    
    # Initialize Pinecone
    pinecone_service.initialize()
    
    # Load embedding model (singleton)
    _ = embedding_service
    
    print("All services initialized successfully!")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await mongodb_service.disconnect()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="RAG-powered chatbot for Hitech Steel Industries",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS middleware for widget embedding
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(lead_router.router)
    app.include_router(chat_router.router)
    app.include_router(ingest_router.router)
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": settings.APP_NAME,
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs"
        }
    
    @app.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "services": {
                "mongodb": "connected" if mongodb_service.db else "disconnected",
                "pinecone": "connected" if pinecone_service._initialized else "disconnected"
            }
        }
    
    return app


# Create app instance
app = create_app()
