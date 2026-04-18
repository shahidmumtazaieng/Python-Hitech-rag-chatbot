"""Lead submission router."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.models.lead import LeadCreate, LeadResponse
from app.services.postgresql_service import PostgreSQLService, get_postgresql_service

router = APIRouter(prefix="/api", tags=["leads"])


@router.post("/lead", response_model=LeadResponse)
async def submit_lead(
    lead: LeadCreate,
    postgresql: PostgreSQLService = Depends(get_postgresql_service)
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
        existing = await postgresql.get_lead_by_email(lead.email)
        if existing:
            # Return existing session
            return LeadResponse(
                success=True,
                sessionId=existing['sessionId'],
                message="Welcome back! Continuing your previous session.",
                lead=existing
            )
        
        # Create new lead
        result = await postgresql.create_lead(lead)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create lead: {str(e)}"
        )


@router.get("/lead/{session_id}")
async def get_lead(
    session_id: str,
    postgresql: PostgreSQLService = Depends(get_postgresql_service)
):
    """Get lead information by session ID."""
    lead = await postgresql.get_lead_by_session(session_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
