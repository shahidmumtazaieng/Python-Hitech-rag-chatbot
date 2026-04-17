"""MongoDB service for leads and conversations."""
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId

from app.config import get_settings
from app.models.lead import LeadCreate, LeadInDB, LeadResponse
from app.models.conversation import Message, Conversation, ConversationCreate, MessageRole


class MongoDBService:
    """Service for MongoDB operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """Connect to MongoDB."""
        import certifi
        import ssl
        
        # Configure SSL/TLS settings for MongoDB Atlas with Windows workaround
        # Python 3.14 on Windows has SSL handshake issues with MongoDB Atlas
        client_options = {
            'tls': True,
            'tlsCAFile': certifi.where(),
            'tlsAllowInvalidHostnames': False,
            'serverSelectionTimeoutMS': 30000,
            'connectTimeoutMS': 30000,
            'socketTimeoutMS': 30000,
            'retryWrites': True,
            'w': 'majority',
            'appname': 'hitech-chatbot'
        }
        
        # Try connection with SSL workaround for Windows
        try:
            self.client = AsyncIOMotorClient(self.settings.MONGODB_URI, **client_options)
            self.db = self.client[self.settings.MONGODB_DB_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            print(f"Connected to MongoDB Atlas: {self.settings.MONGODB_DB_NAME}")
        except Exception as e:
            print(f"Initial connection failed: {e}")
            print("Trying with tlsAllowInvalidCertificates=True as fallback...")
            # Fallback for Windows SSL issues
            client_options['tlsAllowInvalidCertificates'] = True
            self.client = AsyncIOMotorClient(self.settings.MONGODB_URI, **client_options)
            self.db = self.client[self.settings.MONGODB_DB_NAME]
            await self.client.admin.command('ping')
            print(f"Connected to MongoDB Atlas (with SSL fallback): {self.settings.MONGODB_DB_NAME}")
        
        # Create indexes
        await self._create_indexes()
    
    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes."""
        # Leads collection indexes
        await self.db.leads.create_index("sessionId", unique=True)
        await self.db.leads.create_index("email")
        await self.db.leads.create_index("phone")
        await self.db.leads.create_index("createdAt")
        
        # Conversations collection indexes
        await self.db.conversations.create_index("sessionId", unique=True)
        await self.db.conversations.create_index("createdAt")
        await self.db.conversations.create_index("isEscalated")
    
    async def _create_indexes_sync(self):
        """Create database indexes using sync client."""
        # Leads collection indexes
        self._sync_db.leads.create_index("sessionId", unique=True)
        self._sync_db.leads.create_index("email")
        self._sync_db.leads.create_index("phone")
        self._sync_db.leads.create_index("createdAt")
        
        # Conversations collection indexes
        self._sync_db.conversations.create_index("sessionId", unique=True)
        self._sync_db.conversations.create_index("createdAt")
        self._sync_db.conversations.create_index("isEscalated")
    
    # ==================== Lead Operations ====================
    
    async def create_lead(self, lead_data: LeadCreate) -> LeadResponse:
        """Create a new lead and return session info."""
        session_id = str(uuid.uuid4())
        
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
        
        await self.db.leads.insert_one(lead_doc)
        
        # Create empty conversation for this lead
        await self.create_conversation(session_id, lead_doc)
        
        return LeadResponse(
            success=True,
            sessionId=session_id,
            message="Lead created successfully",
            lead=LeadInDB(**lead_doc)
        )
    
    async def get_lead_by_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get lead by session ID."""
        return await self.db.leads.find_one({"sessionId": session_id})
    
    async def get_lead_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get lead by email."""
        return await self.db.leads.find_one({"email": email})
    
    async def update_lead(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update lead information."""
        update_data["updatedAt"] = datetime.utcnow()
        result = await self.db.leads.update_one(
            {"sessionId": session_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    # ==================== Conversation Operations ====================
    
    async def create_conversation(self, session_id: str, lead_info: Dict[str, Any]):
        """Create a new conversation for a lead."""
        conversation_doc = {
            "sessionId": session_id,
            "leadInfo": lead_info,
            "messages": [],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "isEscalated": False,
            "escalationNotes": None
        }
        
        await self.db.conversations.insert_one(conversation_doc)
        return conversation_doc
    
    async def get_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by session ID."""
        return await self.db.conversations.find_one({"sessionId": session_id})
    
    async def add_message(self, session_id: str, role: MessageRole, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation."""
        message = {
            "role": role.value,
            "content": content,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        result = await self.db.conversations.update_one(
            {"sessionId": session_id},
            {
                "$push": {"messages": message},
                "$set": {"updatedAt": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    async def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Message]:
        """Get recent conversation history."""
        conversation = await self.db.conversations.find_one({"sessionId": session_id})
        if not conversation:
            return []
        
        messages = conversation.get("messages", [])
        # Return last N messages
        recent_messages = messages[-limit:] if len(messages) > limit else messages
        
        return [Message(**msg) for msg in recent_messages]
    
    async def get_conversation_context(self, session_id: str, max_messages: int = 10) -> str:
        """Get conversation history formatted as context string."""
        messages = await self.get_conversation_history(session_id, max_messages)
        
        if not messages:
            return ""
        
        context_parts = []
        for msg in messages:
            role_label = "User" if msg.role == MessageRole.USER else "Assistant"
            context_parts.append(f"{role_label}: {msg.content}")
        
        return "\n".join(context_parts)
    
    async def escalate_to_human(self, session_id: str, notes: Optional[str] = None) -> bool:
        """Mark conversation as escalated to human."""
        result = await self.db.conversations.update_one(
            {"sessionId": session_id},
            {
                "$set": {
                    "isEscalated": True,
                    "escalationNotes": notes,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        # Also update lead status
        await self.db.leads.update_one(
            {"sessionId": session_id},
            {"$set": {"status": "escalated", "updatedAt": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    async def cleanup_expired_sessions(self, hours: int = 24):
        """Clean up sessions older than specified hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # This is a maintenance operation - typically run via cron
        result = await self.db.conversations.delete_many({
            "updatedAt": {"$lt": cutoff},
            "isEscalated": False
        })
        
        return result.deleted_count


# Global instance
mongodb_service = MongoDBService()


async def get_mongodb_service() -> MongoDBService:
    """Dependency to get MongoDB service."""
    return mongodb_service
