-- Hitech RAG Chatbot - Neon PostgreSQL Database Schema
-- This schema supports lead storage and conversation persistence

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- LEADS TABLE
-- Stores customer lead information
-- ============================================
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    company VARCHAR(100),
    inquiry_type VARCHAR(50),
    source VARCHAR(50) DEFAULT 'chat_widget',
    status VARCHAR(50) DEFAULT 'new',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for leads table
CREATE INDEX IF NOT EXISTS idx_leads_session_id ON leads(session_id);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);

-- ============================================
-- CONVERSATIONS TABLE
-- Stores conversation metadata and status
-- ============================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL REFERENCES leads(session_id) ON DELETE CASCADE,
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    is_escalated BOOLEAN DEFAULT FALSE,
    escalation_notes TEXT,
    escalation_time TIMESTAMP WITH TIME ZONE,
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for conversations table
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_lead_id ON conversations(lead_id);
CREATE INDEX IF NOT EXISTS idx_conversations_is_escalated ON conversations(is_escalated);
CREATE INDEX IF NOT EXISTS idx_conversations_last_message_at ON conversations(last_message_at);

-- ============================================
-- MESSAGES TABLE
-- Stores individual conversation messages
-- ============================================
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) NOT NULL REFERENCES leads(session_id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    sources JSONB, -- Store RAG sources as JSONB
    metadata JSONB, -- Flexible metadata storage
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for messages table
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_session_created ON messages(session_id, created_at);

-- ============================================
-- KNOWLEDGE BASE DOCUMENTS TABLE (Optional)
-- Tracks ingested documents for the RAG system
-- ============================================
CREATE TABLE IF NOT EXISTS kb_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url VARCHAR(500) NOT NULL,
    title VARCHAR(255),
    content_hash VARCHAR(64), -- SHA-256 hash for deduplication
    chunk_count INTEGER DEFAULT 0,
    pinecone_ids TEXT[], -- Array of Pinecone vector IDs
    last_ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kb_documents_url ON kb_documents(url);
CREATE INDEX IF NOT EXISTS idx_kb_documents_content_hash ON kb_documents(content_hash);

-- ============================================
-- FUNCTIONS AND TRIGGERS
-- ============================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to leads
DROP TRIGGER IF EXISTS update_leads_updated_at ON leads;
CREATE TRIGGER update_leads_updated_at
    BEFORE UPDATE ON leads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply updated_at trigger to conversations
DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to update conversation last_message_at and message_count
CREATE OR REPLACE FUNCTION update_conversation_on_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET 
        last_message_at = NEW.created_at,
        message_count = message_count + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to update conversation stats on new message
DROP TRIGGER IF EXISTS update_conversation_stats ON messages;
CREATE TRIGGER update_conversation_stats
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_on_message();

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- Active conversations view (non-escalated, recent)
CREATE OR REPLACE VIEW active_conversations AS
SELECT 
    c.*,
    l.full_name,
    l.email,
    l.phone,
    l.inquiry_type
FROM conversations c
JOIN leads l ON c.session_id = l.session_id
WHERE c.is_escalated = FALSE
    AND c.last_message_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY c.last_message_at DESC;

-- Escalated conversations view
CREATE OR REPLACE VIEW escalated_conversations AS
SELECT 
    c.*,
    l.full_name,
    l.email,
    l.phone,
    l.inquiry_type
FROM conversations c
JOIN leads l ON c.session_id = l.session_id
WHERE c.is_escalated = TRUE
ORDER BY c.escalation_time DESC;

-- ============================================
-- SAMPLE QUERIES FOR COMMON OPERATIONS
-- ============================================

-- Get conversation with recent messages
-- SELECT * FROM get_conversation_with_messages('session-id-here', 10);

CREATE OR REPLACE FUNCTION get_conversation_with_messages(
    p_session_id VARCHAR,
    p_message_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    session_id VARCHAR,
    lead_name VARCHAR,
    lead_email VARCHAR,
    is_escalated BOOLEAN,
    escalation_notes TEXT,
    messages JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.session_id,
        l.full_name,
        l.email,
        c.is_escalated,
        c.escalation_notes,
        COALESCE(
            JSONB_AGG(
                JSONB_BUILD_OBJECT(
                    'id', m.id,
                    'role', m.role,
                    'content', m.content,
                    'sources', m.sources,
                    'metadata', m.metadata,
                    'timestamp', m.created_at
                ) ORDER BY m.created_at DESC
            ) FILTER (WHERE m.id IS NOT NULL),
            '[]'::JSONB
        ) as messages
    FROM conversations c
    JOIN leads l ON c.session_id = l.session_id
    LEFT JOIN (
        SELECT * FROM messages 
        WHERE messages.session_id = p_session_id
        ORDER BY created_at DESC
        LIMIT p_message_limit
    ) m ON c.session_id = m.session_id
    WHERE c.session_id = p_session_id
    GROUP BY c.session_id, l.full_name, l.email, c.is_escalated, c.escalation_notes;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================

COMMENT ON TABLE leads IS 'Stores customer lead information from chat widget';
COMMENT ON TABLE conversations IS 'Stores conversation metadata and escalation status';
COMMENT ON TABLE messages IS 'Stores individual chat messages with RAG sources';
COMMENT ON COLUMN leads.session_id IS 'Unique session identifier linking lead to conversation';
COMMENT ON COLUMN messages.sources IS 'JSONB array of RAG source documents used for response';
COMMENT ON COLUMN messages.metadata IS 'Flexible JSONB storage for model info, tokens, etc.';
