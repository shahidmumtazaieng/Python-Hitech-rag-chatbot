"""Main FastAPI application for Hitech RAG Chatbot."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.services.postgresql_service import postgresql_service
from app.services.pinecone_service import pinecone_service
from app.services.embedding_service import embedding_service
from app.routers import lead_router, chat_router, ingest_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    settings = get_settings()
    print(f"Starting {settings.APP_NAME}...")
    
    # Connect to PostgreSQL
    await postgresql_service.connect()
    
    # Initialize Pinecone (optional for testing)
    try:
        pinecone_service.initialize()
        print("Pinecone initialized successfully!")
    except Exception as e:
        print(f"Pinecone initialization failed (continuing for testing): {e}")
    
    # Load embedding model (singleton)
    _ = embedding_service
    
    print("All services initialized successfully!")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await postgresql_service.disconnect()


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
        try:
            postgresql_status = "connected" if postgresql_service.engine else "disconnected"
            pinecone_status = "connected" if getattr(pinecone_service, "_initialized", False) else "disconnected"
            return {
                "status": "healthy",
                "services": {
                    "postgresql": postgresql_status,
                    "pinecone": pinecone_status
                }
            }
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"status": "error", "detail": str(e)}
            )
    
    return app


# Create app instance
app = create_app()
