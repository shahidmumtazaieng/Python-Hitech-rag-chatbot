"""PostgreSQL service for leads and conversations using Neon database."""
import re
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean, Integer, ForeignKey, JSON, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from app.config import get_settings
from app.models.lead import LeadCreate, LeadInDB, LeadResponse
from app.models.conversation import MessageRole

from dotenv import load_dotenv
load_dotenv()

Base = declarative_base()


# ---------------------------------------------------------------------------
# ORM models
# ---------------------------------------------------------------------------

class LeadModel(Base):
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

    conversation = relationship(
        "ConversationModel",
        back_populates="lead",
        uselist=False,
        foreign_keys="ConversationModel.lead_id",
    )


class ConversationModel(Base):
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

    lead = relationship("LeadModel", back_populates="conversation", foreign_keys=[lead_id])
    messages = relationship("MessageModel", back_populates="conversation", order_by="MessageModel.created_at")


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), ForeignKey("leads.session_id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    sources = Column(JSON)
    message_metadata = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("ConversationModel", back_populates="messages")


# ---------------------------------------------------------------------------
# Helper: sanitise Neon DATABASE_URL
# ---------------------------------------------------------------------------

def _clean_db_url(url: str) -> str:
    """
    Strip parameters that psycopg2/SQLAlchemy don't understand
    (e.g. channel_binding=require from Neon connection strings).
    """
    url = re.sub(r'[&?]channel_binding=[^&]*', '', url)
    # Fix potential '?&' or trailing '?'
    url = re.sub(r'\?&', '?', url)
    url = re.sub(r'\?$', '', url)
    return url


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class PostgreSQLService:

    def __init__(self):
        self.settings = get_settings()
        self.engine = None
        self.SessionLocal = None
        self._use_mock = False
        self._mock_leads: Dict[str, Dict] = {}
        self._mock_conversations: Dict[str, Dict] = {}
        self._mock_messages: List[Dict] = []

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def connect(self):
        try:
            raw_url = self.settings.DATABASE_URL
            clean_url = _clean_db_url(raw_url)
            print(f"Connecting to PostgreSQL: {clean_url[:60]}…")

            self.engine = create_engine(
                clean_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=300,
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            Base.metadata.create_all(bind=self.engine)
            print("Connected to PostgreSQL successfully.")
        except Exception as exc:
            print(f"PostgreSQL connection failed: {exc}")
            print("Falling back to in-memory mock database.")
            self._use_mock = True

    async def disconnect(self):
        if self.engine:
            self.engine.dispose()
            print("Disconnected from PostgreSQL.")

    def get_db(self) -> Optional[Session]:
        if self.SessionLocal:
            return self.SessionLocal()
        return None

    # ------------------------------------------------------------------
    # Lead operations
    # ------------------------------------------------------------------

    async def create_lead(self, lead_data: LeadCreate) -> LeadResponse:
        # Return existing session if email seen in last 24 h
        existing = await self.get_lead_by_email(lead_data.email)
        if existing:
            return LeadResponse(
                success=True,
                sessionId=existing['sessionId'],
                message="Welcome back! Continuing your previous session.",
                lead=LeadInDB(**{
                    'sessionId': existing['sessionId'],
                    'fullName': existing['fullName'],
                    'email': existing['email'],
                    'phone': existing['phone'],
                    'company': existing.get('company'),
                    'inquiryType': existing.get('inquiryType'),
                    'createdAt': existing['createdAt'],
                    'source': existing.get('source', 'chat_widget'),
                    'status': existing.get('status', 'new'),
                }),
            )

        session_id = str(uuid.uuid4())

        if not self._use_mock:
            db = self.get_db()
            try:
                lead_model = LeadModel(
                    session_id=session_id,
                    full_name=lead_data.fullName,
                    email=lead_data.email,
                    phone=lead_data.phone,
                    company=lead_data.company,
                    inquiry_type=lead_data.inquiryType.value if lead_data.inquiryType else None,
                    source="chat_widget",
                    status="new",
                )
                db.add(lead_model)
                db.commit()
                db.refresh(lead_model)

                conv = ConversationModel(
                    session_id=session_id,
                    lead_id=lead_model.id,
                    is_escalated=False,
                    message_count=0,
                )
                db.add(conv)
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
                        status="new",
                    ),
                )
            finally:
                db.close()
        else:
            doc = {
                "sessionId": session_id,
                "fullName": lead_data.fullName,
                "email": lead_data.email,
                "phone": lead_data.phone,
                "company": lead_data.company,
                "inquiryType": lead_data.inquiryType.value if lead_data.inquiryType else None,
                "createdAt": datetime.utcnow(),
                "source": "chat_widget",
                "status": "new",
            }
            self._mock_leads[session_id] = doc
            self._mock_conversations[session_id] = {
                "sessionId": session_id,
                "isEscalated": False,
                "escalationNotes": None,
                "messageCount": 0,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            }
            return LeadResponse(
                success=True,
                sessionId=session_id,
                message="Lead created successfully",
                lead=LeadInDB(**doc),
            )

    async def get_lead_by_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if not self._use_mock:
            db = self.get_db()
            try:
                lead = db.query(LeadModel).filter(LeadModel.session_id == session_id).first()
                if lead:
                    return self._lead_to_dict(lead)
            finally:
                db.close()
        else:
            return self._mock_leads.get(session_id)
        return None

    async def get_lead_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        if not self._use_mock:
            db = self.get_db()
            try:
                cutoff = datetime.utcnow() - timedelta(hours=24)
                lead = (
                    db.query(LeadModel)
                    .filter(and_(LeadModel.email == email, LeadModel.created_at >= cutoff))
                    .order_by(LeadModel.created_at.desc())
                    .first()
                )
                if lead:
                    return self._lead_to_dict(lead)
            finally:
                db.close()
        else:
            for lead in self._mock_leads.values():
                if lead.get("email") == email:
                    age = datetime.utcnow() - lead.get("createdAt", datetime.utcnow())
                    if age < timedelta(hours=24):
                        return lead
        return None

    def _lead_to_dict(self, lead: LeadModel) -> Dict[str, Any]:
        return {
            "sessionId": lead.session_id,
            "fullName": lead.full_name,
            "email": lead.email,
            "phone": lead.phone,
            "company": lead.company,
            "inquiryType": lead.inquiry_type,
            "createdAt": lead.created_at,
            "source": lead.source,
            "status": lead.status,
        }

    # ------------------------------------------------------------------
    # Conversation operations
    # ------------------------------------------------------------------

    async def get_or_create_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        conv = await self.get_conversation(session_id)
        if conv:
            return conv

        lead = await self.get_lead_by_session(session_id)
        if not lead:
            return None

        if not self._use_mock:
            db = self.get_db()
            try:
                lead_model = db.query(LeadModel).filter(LeadModel.session_id == session_id).first()
                if lead_model:
                    c = ConversationModel(
                        session_id=session_id,
                        lead_id=lead_model.id,
                        is_escalated=False,
                        message_count=0,
                    )
                    db.add(c)
                    db.commit()
                    db.refresh(c)
                    return self._conv_to_dict(c, lead)
            finally:
                db.close()
        else:
            self._mock_conversations[session_id] = {
                "sessionId": session_id,
                "isEscalated": False,
                "escalationNotes": None,
                "messageCount": 0,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            }
            return self._mock_conversations[session_id]
        return None

    async def get_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        if not self._use_mock:
            db = self.get_db()
            try:
                c = db.query(ConversationModel).filter(ConversationModel.session_id == session_id).first()
                if c:
                    lead = await self.get_lead_by_session(session_id)
                    return self._conv_to_dict(c, lead)
            finally:
                db.close()
        else:
            return self._mock_conversations.get(session_id)
        return None

    def _conv_to_dict(self, c: ConversationModel, lead: Optional[Dict]) -> Dict[str, Any]:
        return {
            "id": str(c.id),
            "sessionId": c.session_id,
            "leadInfo": lead,
            "isEscalated": c.is_escalated,
            "escalationNotes": c.escalation_notes,
            "escalationTime": c.escalation_time,
            "lastMessageAt": c.last_message_at,
            "messageCount": c.message_count,
            "createdAt": c.created_at,
            "updatedAt": c.updated_at,
        }

    async def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        sources: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None,
    ):
        if not self._use_mock:
            db = self.get_db()
            try:
                conv = db.query(ConversationModel).filter(ConversationModel.session_id == session_id).first()
                if not conv:
                    lead_model = db.query(LeadModel).filter(LeadModel.session_id == session_id).first()
                    if lead_model:
                        conv = ConversationModel(
                            session_id=session_id,
                            lead_id=lead_model.id,
                            is_escalated=False,
                            message_count=0,
                        )
                        db.add(conv)
                        db.commit()
                        db.refresh(conv)

                if conv:
                    msg = MessageModel(
                        session_id=session_id,
                        conversation_id=conv.id,
                        role=role.value,
                        content=content,
                        sources=sources,
                        message_metadata=metadata,
                    )
                    db.add(msg)
                    conv.message_count = (conv.message_count or 0) + 1
                    conv.last_message_at = datetime.utcnow()
                    db.commit()
            finally:
                db.close()
        else:
            self._mock_messages.append({
                "sessionId": session_id,
                "role": role.value,
                "content": content,
                "sources": sources,
                "metadata": metadata,
                "timestamp": datetime.utcnow(),
            })
            if session_id in self._mock_conversations:
                self._mock_conversations[session_id]["messageCount"] = (
                    self._mock_conversations[session_id].get("messageCount", 0) + 1
                )

    async def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        if not self._use_mock:
            db = self.get_db()
            try:
                msgs = (
                    db.query(MessageModel)
                    .filter(MessageModel.session_id == session_id)
                    .order_by(MessageModel.created_at.desc())
                    .limit(limit)
                    .all()
                )
                return [
                    {
                        "role": m.role,
                        "content": m.content,
                        "timestamp": m.created_at,
                        "sources": m.sources,
                        "metadata": m.message_metadata,
                    }
                    for m in reversed(msgs)
                ]
            finally:
                db.close()
        else:
            msgs = [m for m in self._mock_messages if m.get("sessionId") == session_id]
            msgs.sort(key=lambda x: x.get("timestamp", datetime.utcnow()))
            return msgs[-limit:]

    async def get_conversation_messages(self, session_id: str, limit: int = 50) -> List[Dict]:
        if not self._use_mock:
            db = self.get_db()
            try:
                msgs = (
                    db.query(MessageModel)
                    .filter(MessageModel.session_id == session_id)
                    .order_by(MessageModel.created_at.desc())
                    .limit(limit)
                    .all()
                )
                return [
                    {
                        "id": str(m.id),
                        "role": m.role,
                        "content": m.content,
                        "sources": m.sources,
                        "metadata": m.message_metadata,
                        "timestamp": m.created_at.isoformat() if m.created_at else None,
                    }
                    for m in reversed(msgs)
                ]
            finally:
                db.close()
        else:
            msgs = [m for m in self._mock_messages if m.get("sessionId") == session_id]
            msgs.sort(key=lambda x: x.get("timestamp", datetime.utcnow()))
            return msgs[-limit:]

    async def escalate_to_human(self, session_id: str, notes: Optional[str] = None) -> bool:
        if not self._use_mock:
            db = self.get_db()
            try:
                conv = db.query(ConversationModel).filter(ConversationModel.session_id == session_id).first()
                if conv:
                    conv.is_escalated = True
                    conv.escalation_notes = notes
                    conv.escalation_time = datetime.utcnow()
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
                return True
        return False

    async def check_session_valid(self, session_id: str) -> bool:
        lead = await self.get_lead_by_session(session_id)
        if not lead:
            return False
        created_at = lead.get("createdAt")
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age = datetime.utcnow() - created_at.replace(tzinfo=None)
            return age < timedelta(hours=24)
        return True

    async def get_lead_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        lead = await self.get_lead_by_session(session_id)
        conversation = await self.get_conversation(session_id)
        messages = await self.get_conversation_messages(session_id, limit=20)
        return {
            "lead": lead,
            "conversation": conversation,
            "messages": messages,
            "hasActiveSession": lead is not None and await self.check_session_valid(session_id),
        }


# Singleton
postgresql_service = PostgreSQLService()


def get_postgresql_service() -> PostgreSQLService:
    return postgresql_service