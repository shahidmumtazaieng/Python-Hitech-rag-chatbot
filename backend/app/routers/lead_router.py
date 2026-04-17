"""Lead submission router."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.models.lead import LeadCreate, LeadResponse
from app.services.mongodb_service import MongoDBService, get_mongodb_service

router = APIRouter(prefix="/api", tags=["leads"])


@router.post("/lead", response_model=LeadResponse)
async def submit_lead(
    lead: LeadCreate,
    mongodb: MongoDBService = Depends(get_mongodb_service)
) -> LeadResponse:
    """
    Submit a new lead and create a chat session.
    
    - Validates lead information
    - Creates session ID
    - Stores lead in MongoDB
    - Initializes empty conversation
    """
    try:
        # Check if email already exists with active session
        existing = await mongodb.get_lead_by_email(lead.email)
        if existing:
            # Return existing session
            return LeadResponse(
                success=True,
                sessionId=existing['sessionId'],
                message="Welcome back! Continuing your previous session.",
                lead=existing
            )
        
        # Create new lead
        result = await mongodb.create_lead(lead)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create lead: {str(e)}"
        )


@router.get("/lead/{session_id}")
async def get_lead(
    session_id: str,
    mongodb: MongoDBService = Depends(get_mongodb_service)
):
    """Get lead information by session ID."""
    lead = await mongodb.get_lead_by_session(session_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
