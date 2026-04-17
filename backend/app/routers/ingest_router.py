"""Knowledgebase ingestion router."""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from app.services.scraper_service import ScraperService, get_scraper_service
from app.services.pinecone_service import PineconeService, get_pinecone_service

router = APIRouter(prefix="/api", tags=["ingestion"])


class IngestRequest(BaseModel):
    """Request body for ingestion."""
    url: Optional[str] = None
    max_pages: Optional[int] = 50


class IngestResponse(BaseModel):
    """Response from ingestion."""
    status: str
    message: str
    pages_scraped: Optional[int] = None
    chunks_created: Optional[int] = None


@router.post("/ingest", response_model=IngestResponse)
async def ingest_knowledgebase(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    scraper: ScraperService = Depends(get_scraper_service),
    pinecone: PineconeService = Depends(get_pinecone_service)
):
    """
    Trigger knowledgebase ingestion from website.
    
    - Scrapes website recursively
    - Chunks content
    - Generates embeddings
    - Stores in Pinecone
    
    Note: This can take several minutes for large sites.
    """
    try:
        # Run ingestion synchronously for now (can be made async)
        pages = scraper.scrape_website(
            base_url=request.url,
            max_pages=request.max_pages
        )
        
        if not pages:
            return IngestResponse(
                status="warning",
                message="No pages were scraped. Check the URL and try again."
            )
        
        # Ingest to Pinecone
        result = scraper.ingest_to_pinecone(pages)
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=result.get('message'))
        
        return IngestResponse(
            status="success",
            message=f"Successfully ingested {result['pages_scraped']} pages with {result['chunks_created']} chunks",
            pages_scraped=result.get('pages_scraped'),
            chunks_created=result.get('chunks_created')
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}"
        )


@router.get("/ingest/status")
async def get_ingest_status(
    pinecone: PineconeService = Depends(get_pinecone_service)
):
    """Get vector store statistics."""
    try:
        stats = pinecone.get_stats()
        return {
            "status": "active",
            "vector_store": "pinecone",
            **stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get status: {str(e)}"
        )


@router.delete("/ingest/clear")
async def clear_knowledgebase(
    pinecone: PineconeService = Depends(get_pinecone_service)
):
    """Clear all vectors from the knowledgebase."""
    try:
        result = pinecone.delete_all()
        return {
            "status": "success",
            "message": "Knowledgebase cleared successfully",
            **result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear knowledgebase: {str(e)}"
        )
