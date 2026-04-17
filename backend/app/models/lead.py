"""Lead data models."""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class InquiryType(str, Enum):
    """Types of customer inquiries."""
    PRODUCT_INFO = "Product Information"
    PRICING_QUOTE = "Pricing Quote"
    TECHNICAL_SUPPORT = "Technical Support"
    PARTNERSHIP = "Partnership"
    CAREERS = "Careers"
    OTHER = "Other"


class LeadBase(BaseModel):
    """Base lead model with common fields."""
    fullName: str = Field(..., min_length=2, max_length=100, description="Customer full name")
    email: EmailStr = Field(..., description="Customer email address")
    phone: str = Field(..., min_length=10, max_length=20, description="Saudi phone number")
    company: Optional[str] = Field(None, max_length=100, description="Company name (optional)")
    inquiryType: Optional[InquiryType] = Field(None, description="Type of inquiry")
    
    @field_validator('phone')
    @classmethod
    def validate_saudi_phone(cls, v: str) -> str:
        """Validate Saudi phone number format."""
        cleaned = v.replace(' ', '').replace('-', '')
        # Accept formats: +9665xxxxxxxx, 9665xxxxxxxx, 05xxxxxxxx
        if not any([
            cleaned.startswith('+9665') and len(cleaned) == 13,
            cleaned.startswith('9665') and len(cleaned) == 12,
            cleaned.startswith('05') and len(cleaned) == 10,
        ]):
            raise ValueError('Invalid Saudi phone number format. Use +966 5xxxxxxxx or 05xxxxxxxx')
        return cleaned


class LeadCreate(LeadBase):
    """Model for creating a new lead."""
    pass


class LeadInDB(LeadBase):
    """Lead model as stored in database."""
    sessionId: str = Field(..., description="Unique session identifier")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = None
    source: str = Field(default="chat_widget", description="Lead source")
    status: str = Field(default="new", description="Lead status")
    
    class Config:
        populate_by_name = True


class LeadResponse(BaseModel):
    """Response model for lead submission."""
    success: bool
    sessionId: str
    message: str
    lead: Optional[LeadInDB] = None
