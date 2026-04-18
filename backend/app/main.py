"""Main FastAPI application for Hitech RAG Chatbot."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.services.postgresql_service import postgresql_service
from app.services.pinecone_service import pinecone_service
from app.services.embedding_service import embedding_service
from app.routers import lead_router, chat_router, ingest_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"Starting {settings.APP_NAME}…")

    await postgresql_service.connect()

    try:
        pinecone_service.initialize()
        print("Pinecone initialised successfully.")
    except Exception as exc:
        print(f"Pinecone initialisation failed (non-fatal): {exc}")

    # Warm up embedding model (singleton)
    _ = embedding_service
    print("All services ready.")

    yield

    print("Shutting down…")
    await postgresql_service.disconnect()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description="RAG-powered chatbot for Hitech Steel Industries",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(lead_router.router)
    app.include_router(chat_router.router)
    app.include_router(ingest_router.router)

    @app.get("/")
    async def root():
        return {"name": settings.APP_NAME, "version": "1.0.0", "status": "running", "docs": "/docs"}

    @app.get("/api/health")
    async def health_check():
        try:
            return {
                "status": "healthy",
                "services": {
                    "postgresql": "connected" if postgresql_service.engine else "disconnected",
                    "pinecone": "connected" if getattr(pinecone_service, "_initialized", False) else "disconnected",
                },
            }
        except Exception as exc:
            return JSONResponse(status_code=500, content={"status": "error", "detail": str(exc)})

    return app


app = create_app()