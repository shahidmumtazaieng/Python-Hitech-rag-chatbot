# Hitech RAG Chatbot - PostgreSQL Database Setup Guide

This guide explains how to set up the Neon PostgreSQL database for the Hitech RAG Chatbot, replacing the previous MongoDB implementation.

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Next.js       │────▶│   FastAPI        │────▶│   Neon Postgre  │
│   Frontend      │     │   Backend        │     │   SQL           │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                           │
                               ▼                           ▼
                        ┌──────────────┐           ┌──────────────┐
                        │   Pinecone   │           │   Tables:    │
                        │   Vector DB  │           │   - leads    │
                        │              │           │   - convos   │
                        │   BGE-M3     │           │   - messages │
                        │   Embeddings │           └──────────────┘
                        └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │   Gemini     │
                        │   2.5 Flash  │
                        └──────────────┘
```

## Database Schema

### Tables

#### 1. `leads` - Customer Information
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| session_id | VARCHAR(255) | Unique session identifier |
| full_name | VARCHAR(100) | Customer name |
| email | VARCHAR(255) | Customer email |
| phone | VARCHAR(20) | Saudi phone number |
| company | VARCHAR(100) | Company name (optional) |
| inquiry_type | VARCHAR(50) | Type of inquiry |
| source | VARCHAR(50) | Lead source (default: chat_widget) |
| status | VARCHAR(50) | Lead status (new, escalated, etc.) |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

#### 2. `conversations` - Conversation Metadata
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| session_id | VARCHAR(255) | Links to leads.session_id |
| lead_id | UUID | Links to leads.id |
| is_escalated | BOOLEAN | Whether escalated to human |
| escalation_notes | TEXT | Notes for human agent |
| escalation_time | TIMESTAMP | When escalated |
| last_message_at | TIMESTAMP | Last activity |
| message_count | INTEGER | Total message count |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

#### 3. `messages` - Individual Messages
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| session_id | VARCHAR(255) | Links to leads.session_id |
| conversation_id | UUID | Links to conversations.id |
| role | VARCHAR(20) | user/assistant/system |
| content | TEXT | Message content |
| sources | JSONB | RAG source documents |
| metadata | JSONB | Model info, tokens, etc. |
| created_at | TIMESTAMP | Message timestamp |

## Setup Instructions

### Step 1: Create Neon PostgreSQL Database

1. Go to [https://neon.tech](https://neon.tech) and sign up
2. Create a new project
3. Create a database named `hitech_chatbot`
4. Copy the connection string (it looks like):
   ```
   postgresql://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/hitech_chatbot?sslmode=require
   ```

### Step 2: Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Required: PostgreSQL Connection
DATABASE_URL="postgresql://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/hitech_chatbot?sslmode=require"

# Required: Pinecone Vector Store
PINECONE_API_KEY="your-pinecone-api-key"
PINECONE_INDEX_NAME="hitech-kb-index"
PINECONE_HOST="https://your-index.svc.environment.pinecone.io"

# Required: Google Gemini
GEMINI_API_KEY="your-gemini-api-key"
```

### Step 3: Initialize Database

Run the database initialization script:

```bash
cd backend

# Create virtual environment if not exists
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# OR Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_database.py
```

You should see output like:
```
🔧 Hitech RAG Chatbot - Database Initialization
============================================================

📡 Connecting to database...
✅ Connected to PostgreSQL
   Version: PostgreSQL 15.4 on x86_64-pc-linux-gnu...

📦 Creating tables...
   ✓ Table 'leads' created/verified
   ✓ Table 'conversations' created/verified
   ✓ Table 'messages' created/verified

🔍 Creating indexes and triggers...
   ✓ Indexes created
   ✓ Trigger function created
   ✓ Triggers created
   ✓ Stats trigger function created
   ✓ Stats trigger created
   ✓ Helper function created

============================================================
✅ Database initialization complete!

📊 Tables created:
   • leads
   • conversations
   • messages

🚀 Your database is ready to use!
```

### Step 4: Verify Database

```bash
python init_database.py --verify
```

## Session Management Flow

### User Returns Within 24 Hours

```
1. User opens chat widget
2. Frontend checks localStorage for sessionId
3. Frontend calls POST /api/session/check
4. Backend validates session in PostgreSQL
5. If valid, frontend calls POST /api/session/restore
6. Backend returns lead info + conversation history
7. User continues chat without re-submitting lead form
```

### User Returns After 24 Hours

```
1. User opens chat widget
2. Frontend finds expired session in localStorage
3. Frontend clears localStorage
4. User sees lead form again
5. New session created on submission
```

## API Endpoints for Session Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/lead` | POST | Submit lead form, create new session |
| `/api/session/check` | POST | Check if session is valid |
| `/api/session/restore` | POST | Restore session with history |
| `/api/chat/sync` | POST | Send message, get RAG response |
| `/api/talk-to-human` | POST | Escalate to human agent |
| `/api/conversation/{id}` | GET | Get full conversation details |

## Key Features

### 1. Automatic Session Restoration
- Sessions valid for 24 hours
- No need to re-enter lead information
- Full conversation history restored

### 2. Conversation Persistence
- All messages stored in PostgreSQL
- RAG sources preserved with each message
- Human escalation tracked

### 3. Lead Deduplication
- Email-based duplicate detection
- Returns existing session if within 24 hours
- Prevents duplicate lead entries

### 4. Database Triggers
- Auto-updates `updated_at` timestamps
- Auto-increments message count
- Auto-updates `last_message_at`

## Troubleshooting

### Connection Issues

```bash
# Test connection
python -c "
import os
os.environ['DATABASE_URL'] = 'your-connection-string'
from app.services.postgresql_service import postgresql_service
import asyncio
asyncio.run(postgresql_service.connect())
"
```

### Reset Database

**⚠️ WARNING: This will delete all data!**

```bash
# Drop and recreate tables
python -c "
from sqlalchemy import create_engine
from app.services.postgresql_service import Base
import os

engine = create_engine(os.getenv('DATABASE_URL'))
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print('Database reset complete')
"
```

### Check Database Status

```sql
-- View lead count
SELECT COUNT(*) FROM leads;

-- View active conversations (last 24h)
SELECT * FROM active_conversations;

-- View escalated conversations
SELECT * FROM escalated_conversations;

-- Get conversation with messages
SELECT * FROM get_conversation_with_messages('session-id-here', 10);
```

## Migration from MongoDB

If you're migrating from the previous MongoDB implementation:

1. Export MongoDB data:
   ```bash
   mongodump --uri="your-mongodb-uri" --out=mongodb_backup
   ```

2. Transform and import to PostgreSQL (custom script needed based on your data)

3. Update environment variables:
   - Remove `MONGODB_URI`
   - Add `DATABASE_URL`

4. Deploy new backend version

## Performance Notes

- **Connection Pooling**: 5 connections, max 10 overflow
- **Indexes**: All query patterns are indexed
- **JSONB**: Sources and metadata use efficient binary JSON
- **Triggers**: Automatic stats updates reduce query complexity

## Support

For issues with:
- **Neon**: https://neon.tech/docs/introduction
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **This project**: Check the main README.md
