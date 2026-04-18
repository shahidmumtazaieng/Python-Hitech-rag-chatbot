"""PostgreSQL service for leads and conversations using Neon database."""
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean, Integer, ForeignKey, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from app.config import get_settings
from app.models.lead import LeadCreate, LeadInDB, LeadResponse, InquiryType
from app.models.conversation import MessageRole
from dotenv import load_dotenv
load_dotenv()

Base = declarative_base()


class LeadModel(Base):
    """SQLAlchemy model for leads."""
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    company = Column(String(100))
    inquiry_type = Column(String(50))
    source = Column(String(50), default="chat_widget")
    status = Column(String(50), default="new")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship - specify foreign_keys to avoid ambiguity
    conversation = relationship(
        "ConversationModel", 
        back_populates="lead", 
        uselist=False,
        foreign_keys="ConversationModel.lead_id"
    )


class ConversationModel(Base):
    """SQLAlchemy model for conversations."""
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), ForeignKey("leads.session_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"))
    is_escalated = Column(Boolean, default=False)
    escalation_notes = Column(Text)
    escalation_time = Column(DateTime(timezone=True))
    last_message_at = Column(DateTime(timezone=True), server_default=func.now())
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship - specify foreign_keys to avoid ambiguity
    lead = relationship(
        "LeadModel", 
        back_populates="conversation",
        foreign_keys=[lead_id]
    )
    messages = relationship("MessageModel", back_populates="conversation", order_by="MessageModel.created_at")


class MessageModel(Base):
    """SQLAlchemy model for messages."""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), ForeignKey("leads.session_id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    sources = Column(JSON)  # RAG sources
    message_metadata = Column("metadata", JSON)  # Flexible metadata (renamed to avoid SQLAlchemy reserved word)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    conversation = relationship("ConversationModel", back_populates="messages")


class PostgreSQLService:
    """Service for PostgreSQL operations using Neon."""

    def __init__(self):
        self.settings = get_settings()
        self.engine = None
        self.SessionLocal = None
        self._use_mock = False
        self._mock_leads: Dict[str, Dict] = {}
        self._mock_conversations: Dict[str, Dict] = {}
        self._mock_messages: List[Dict] = []

    async def connect(self):
        """Connect to PostgreSQL database."""
        try:
            print(f"Connecting to PostgreSQL at: {self.settings.DATABASE_URL[:50]}...")

            # Create engine for SQLAlchemy with connection pooling
            self.engine = create_engine(
                self.settings.DATABASE_URL,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=300
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            # Create tables
            Base.metadata.create_all(bind=self.engine)

            print("Connected to PostgreSQL database successfully")
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            print("Falling back to in-memory mock database for testing...")
            self._use_mock = True

    def get_db(self) -> Optional[Session]:
        """Get database session."""
        if self.SessionLocal:
            return self.SessionLocal()
        return None

    async def disconnect(self):
        """Disconnect from PostgreSQL."""
        if self.engine:
            self.engine.dispose()
            print("Disconnected from PostgreSQL")

    # ==================== Lead Operations ====================

    async def create_lead(self, lead_data: LeadCreate) -> LeadResponse:
        """Create a new lead and return session info."""
        # Check if email already exists with active session
        existing_lead = await self.get_lead_by_email(lead_data.email)
        if existing_lead:
            # Return existing session
            return LeadResponse(
                success=True,
                sessionId=existing_lead['sessionId'],
                message="Welcome back! Continuing your previous session.",
                lead=LeadInDB(**existing_lead)
            )
        
        session_id = str(uuid.uuid4())

        if not self._use_mock:
            # Use PostgreSQL
            db = self.get_db()
            try:
                # Create lead
                lead_model = LeadModel(
                    session_id=session_id,
                    full_name=lead_data.fullName,
                    email=lead_data.email,
                    phone=lead_data.phone,
                    company=lead_data.company,
                    inquiry_type=lead_data.inquiryType.value if lead_data.inquiryType else None,
                    source="chat_widget",
                    status="new"
                )

                db.add(lead_model)
                db.commit()
                db.refresh(lead_model)

                # Create conversation record
                conversation = ConversationModel(
                    session_id=session_id,
                    lead_id=lead_model.id,
                    is_escalated=False,
                    message_count=0
                )
                db.add(conversation)
                db.commit()

                return LeadResponse(
                    success=True,
                    sessionId=session_id,
                    message="Lead created successfully",
                    lead=LeadInDB(
                        sessionId=session_id,
                        fullName=lead_data.fullName,
                        email=lead_data.email,
                        phone=lead_data.phone,
                        company=lead_data.company,
                        inquiryType=lead_data.inquiryType,
                        createdAt=lead_model.created_at,
                        source="chat_widget",
                        status="new"
                    )
                )
            finally:
                db.close()
        else:
            # Fallback to in-memory
            lead_doc = {
                "sessionId": session_id,
                "fullName": lead_data.fullName,
                "email": lead_data.email,
                "phone": lead_data.phone,
                "company": lead_data.company,
                "inquiryType": lead_data.inquiryType.value if lead_data.inquiryType else None,
                "createdAt": datetime.utcnow(),
                "source": "chat_widget",
                "status": "new"
            }

            self._mock_leads[session_id] = lead_doc
            self._mock_conversations[session_id] = {
                "sessionId": session_id,
                "isEscalated": False,
                "escalationNotes": None,
                "messageCount": 0,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }

            return LeadResponse(
                success=True,
                sessionId=session_id,
                message="Lead created successfully",
                lead=LeadInDB(**lead_doc)
            )

    async def get_lead_by_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get lead by session ID."""
        if not self._use_mock:
            db = self.get_db()
            try:
                lead = db.query(LeadModel).filter(LeadModel.session_id == session_id).first()
                if lead:
                    return {
                        "sessionId": lead.session_id,
                        "fullName": lead.full_name,
                        "email": lead.email,
                        "phone": lead.phone,
                        "company": lead.company,
                        "inquiryType": lead.inquiry_type,
                        "createdAt": lead.created_at,
                        "source": lead.source,
                        "status": lead.status
                    }
            finally:
                db.close()
        else:
            # Fallback to in-memory
            return self._mock_leads.get(session_id)
        return None

    async def get_lead_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get lead by email - checks for active sessions within last 24 hours."""
        if not self._use_mock:
            db = self.get_db()
            try:
                # Get lead with recent activity (within 24 hours)
                from sqlalchemy import and_
                twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
                
                lead = db.query(LeadModel).filter(
                    and_(
                        LeadModel.email == email,
                        LeadModel.created_at >= twenty_four_hours_ago
                    )
                ).order_by(LeadModel.created_at.desc()).first()
                
                if lead:
                    return {
                        "sessionId": lead.session_id,
                        "fullName": lead.full_name,
                        "email": lead.email,
                        "phone": lead.phone,
                        "company": lead.company,
                        "inquiryType": lead.inquiry_type,
                        "createdAt": lead.created_at,
                        "source": lead.source,
                        "status": lead.status
                    }
            finally:
                db.close()
        else:
            # Fallback to in-memory
            for lead in self._mock_leads.values():
                if lead.get("email") == email:
                    age = datetime.utcnow() - lead.get("createdAt", datetime.utcnow())
                    if age < timedelta(hours=24):
                        return lead
        return None

    # ==================== Conversation Operations ====================

    async def get_or_create_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get existing conversation or create new one."""
        conversation = await self.get_conversation(session_id)
        if conversation:
            return conversation
        
        # Create new conversation if lead exists
        lead = await self.get_lead_by_session(session_id)
        if not lead:
            return None
            
        if not self._use_mock:
            db = self.get_db()
            try:
                lead_model = db.query(LeadModel).filter(LeadModel.session_id == session_id).first()
                if lead_model:
                    conversation = ConversationModel(
                        session_id=session_id,
                        lead_id=lead_model.id,
                        is_escalated=False,
                        message_count=0
                    )
                    db.add(conversation)
                    db.commit()
                    db.refresh(conversation)
                    return {
                        "id": str(conversation.id),
                        "sessionId": conversation.session_id,
                        "isEscalated": conversation.is_escalated,
                        "escalationNotes": conversation.escalation_notes,
                        "messageCount": conversation.message_count,
                        "createdAt": conversation.created_at,
                        "updatedAt": conversation.updated_at
                    }
            finally:
                db.close()
        else:
            self._mock_conversations[session_id] = {
                "sessionId": session_id,
                "isEscalated": False,
                "escalationNotes": None,
                "messageCount": 0,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            return self._mock_conversations[session_id]
        return None

    async def get_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by session ID with lead info."""
        if not self._use_mock:
            db = self.get_db()
            try:
                conversation = db.query(ConversationModel).filter(
                    ConversationModel.session_id == session_id
                ).first()
                
                if conversation:
                    lead = await self.get_lead_by_session(session_id)
                    return {
                        "id": str(conversation.id),
                        "sessionId": conversation.session_id,
                        "leadInfo": lead,
                        "isEscalated": conversation.is_escalated,
                        "escalationNotes": conversation.escalation_notes,
                        "escalationTime": conversation.escalation_time,
                        "lastMessageAt": conversation.last_message_at,
                        "messageCount": conversation.message_count,
                        "createdAt": conversation.created_at,
                        "updatedAt": conversation.updated_at
                    }
            finally:
                db.close()
        else:
            return self._mock_conversations.get(session_id)
        return None

    async def add_message(
        self, 
        session_id: str, 
        role: MessageRole, 
        content: str, 
        sources: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ):
        """Add a message to the conversation."""
        if not self._use_mock:
            db = self.get_db()
            try:
                # Get conversation
                conversation = db.query(ConversationModel).filter(
                    ConversationModel.session_id == session_id
                ).first()
                
                if not conversation:
                    # Create conversation if doesn't exist
                    lead_model = db.query(LeadModel).filter(LeadModel.session_id == session_id).first()
                    if lead_model:
                        conversation = ConversationModel(
                            session_id=session_id,
                            lead_id=lead_model.id,
                            is_escalated=False,
                            message_count=0
                        )
                        db.add(conversation)
                        db.commit()
                        db.refresh(conversation)
                
                if conversation:
                    # Create message
                    message = MessageModel(
                        session_id=session_id,
                        conversation_id=conversation.id,
                        role=role.value,
                        content=content,
                        sources=sources,
                        message_metadata=metadata
                    )
                    db.add(message)
                    
                    # Update conversation stats
                    conversation.message_count += 1
                    conversation.last_message_at = datetime.utcnow()
                    
                    db.commit()
            finally:
                db.close()
        else:
            # In-memory fallback
            self._mock_messages.append({
                "sessionId": session_id,
                "role": role.value,
                "content": content,
                "sources": sources,
                "metadata": metadata,
                "timestamp": datetime.utcnow()
            })
            if session_id in self._mock_conversations:
                self._mock_conversations[session_id]["messageCount"] += 1
                self._mock_conversations[session_id]["updatedAt"] = datetime.utcnow()

    async def get_conversation_history(
        self, 
        session_id: str, 
        limit: int = 10
    ) -> List[Dict]:
        """Get recent conversation history formatted for RAG."""
        if not self._use_mock:
            db = self.get_db()
            try:
                messages = db.query(MessageModel).filter(
                    MessageModel.session_id == session_id
                ).order_by(MessageModel.created_at.desc()).limit(limit).all()
                
                # Return in chronological order
                return [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.created_at,
                        "sources": msg.sources,
                        "metadata": msg.message_metadata
                    }
                    for msg in reversed(messages)
                ]
            finally:
                db.close()
        else:
            # In-memory fallback
            messages = [
                msg for msg in self._mock_messages 
                if msg.get("sessionId") == session_id
            ]
            messages.sort(key=lambda x: x.get("timestamp", datetime.utcnow()))
            return messages[-limit:] if len(messages) > limit else messages

    async def get_conversation_messages(
        self, 
        session_id: str, 
        limit: int = 50
    ) -> List[Dict]:
        """Get full conversation messages with all details."""
        if not self._use_mock:
            db = self.get_db()
            try:
                messages = db.query(MessageModel).filter(
                    MessageModel.session_id == session_id
                ).order_by(MessageModel.created_at.desc()).limit(limit).all()
                
                return [
                    {
                        "id": str(msg.id),
                        "role": msg.role,
                        "content": msg.content,
                        "sources": msg.sources,
                        "metadata": msg.message_metadata,
                        "timestamp": msg.created_at.isoformat() if msg.created_at else None
                    }
                    for msg in reversed(messages)
                ]
            finally:
                db.close()
        else:
            messages = [
                msg for msg in self._mock_messages 
                if msg.get("sessionId") == session_id
            ]
            messages.sort(key=lambda x: x.get("timestamp", datetime.utcnow()))
            return messages[-limit:] if len(messages) > limit else messages

    async def escalate_to_human(
        self, 
        session_id: str, 
        notes: Optional[str] = None
    ) -> bool:
        """Mark conversation as escalated to human."""
        if not self._use_mock:
            db = self.get_db()
            try:
                conversation = db.query(ConversationModel).filter(
                    ConversationModel.session_id == session_id
                ).first()
                
                if conversation:
                    conversation.is_escalated = True
                    conversation.escalation_notes = notes
                    conversation.escalation_time = datetime.utcnow()
                    
                    # Update lead status
                    lead = db.query(LeadModel).filter(LeadModel.session_id == session_id).first()
                    if lead:
                        lead.status = "escalated"
                    
                    db.commit()
                    return True
            finally:
                db.close()
        else:
            if session_id in self._mock_conversations:
                self._mock_conversations[session_id]["isEscalated"] = True
                self._mock_conversations[session_id]["escalationNotes"] = notes
                self._mock_conversations[session_id]["updatedAt"] = datetime.utcnow()
                return True
        return False

    async def check_session_valid(self, session_id: str) -> bool:
        """Check if session exists and is not expired (24 hours)."""
        lead = await self.get_lead_by_session(session_id)
        if not lead:
            return False
        
        # Check if session is older than 24 hours
        created_at = lead.get("createdAt")
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age = datetime.utcnow() - created_at.replace(tzinfo=None)
            return age < timedelta(hours=24)
        return True

    async def get_lead_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get complete lead and conversation summary."""
        lead = await self.get_lead_by_session(session_id)
        conversation = await self.get_conversation(session_id)
        messages = await self.get_conversation_messages(session_id, limit=20)
        
        return {
            "lead": lead,
            "conversation": conversation,
            "messages": messages,
            "hasActiveSession": lead is not None and await self.check_session_valid(session_id)
        }


# Global instance
postgresql_service = PostgreSQLService()


def get_postgresql_service() -> PostgreSQLService:
    """Dependency to get PostgreSQL service."""
    return postgresql_service