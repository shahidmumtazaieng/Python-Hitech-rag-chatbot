#!/usr/bin/env python3
"""
Database initialization script for Hitech RAG Chatbot.
Creates all tables, indexes, and triggers in Neon PostgreSQL.

Usage:
    python init_database.py
    
Environment Variables:
    DATABASE_URL - PostgreSQL connection string (required)
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.postgresql_service import Base, LeadModel, ConversationModel


def init_database():
    """Initialize database with all tables, indexes, and triggers."""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable not set")
        print("\nPlease set your Neon PostgreSQL connection string:")
        print("  export DATABASE_URL='postgresql://user:password@host:port/database'")
        sys.exit(1)
    
    print("🔧 Hitech RAG Chatbot - Database Initialization")
    print("=" * 60)
    print(f"\n📡 Connecting to database...")
    
    try:
        # Create engine
        engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL")
            print(f"   Version: {version[:50]}...")
        
        # Create all tables
        print("\n📦 Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        tables = ["leads", "conversations", "messages"]
        for table in tables:
            print(f"   ✓ Table '{table}' created/verified")
        
        # Create additional indexes and triggers via raw SQL
        print("\n🔍 Creating indexes and triggers...")
        
        with engine.connect() as conn:
            # Create indexes
            indexes_sql = """
                -- Leads indexes
                CREATE INDEX IF NOT EXISTS idx_leads_session_id ON leads(session_id);
                CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
                CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
                CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);
                
                -- Conversations indexes
                CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
                CREATE INDEX IF NOT EXISTS idx_conversations_lead_id ON conversations(lead_id);
                CREATE INDEX IF NOT EXISTS idx_conversations_is_escalated ON conversations(is_escalated);
                CREATE INDEX IF NOT EXISTS idx_conversations_last_message_at ON conversations(last_message_at);
                
                -- Messages indexes
                CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
                CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
                CREATE INDEX IF NOT EXISTS idx_messages_session_created ON messages(session_id, created_at);
            """
            
            conn.execute(text(indexes_sql))
            conn.commit()
            print("   ✓ Indexes created")
            
            # Create trigger function
            trigger_function_sql = """
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """
            conn.execute(text(trigger_function_sql))
            conn.commit()
            print("   ✓ Trigger function created")
            
            # Create triggers
            triggers_sql = """
                DROP TRIGGER IF EXISTS update_leads_updated_at ON leads;
                CREATE TRIGGER update_leads_updated_at
                    BEFORE UPDATE ON leads
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
                
                DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
                CREATE TRIGGER update_conversations_updated_at
                    BEFORE UPDATE ON conversations
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
            """
            conn.execute(text(triggers_sql))
            conn.commit()
            print("   ✓ Triggers created")
            
            # Create conversation stats update function
            stats_function_sql = """
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
            """
            conn.execute(text(stats_function_sql))
            conn.commit()
            print("   ✓ Stats trigger function created")
            
            # Create stats trigger
            stats_trigger_sql = """
                DROP TRIGGER IF EXISTS update_conversation_stats ON messages;
                CREATE TRIGGER update_conversation_stats
                    AFTER INSERT ON messages
                    FOR EACH ROW
                    EXECUTE FUNCTION update_conversation_on_message();
            """
            conn.execute(text(stats_trigger_sql))
            conn.commit()
            print("   ✓ Stats trigger created")
            
            # Create helper function for getting conversation with messages
            helper_function_sql = """
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
            """
            conn.execute(text(helper_function_sql))
            conn.commit()
            print("   ✓ Helper function created")
        
        print("\n" + "=" * 60)
        print("✅ Database initialization complete!")
        print("\n📊 Tables created:")
        for table in tables:
            print(f"   • {table}")
        print("\n🚀 Your database is ready to use!")
        
    except SQLAlchemyError as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


def verify_database():
    """Verify database connection and tables."""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            
            required_tables = ['leads', 'conversations', 'messages']
            missing = [t for t in required_tables if t not in tables]
            
            if missing:
                print(f"❌ Missing tables: {', '.join(missing)}")
                return False
            
            # Check row counts
            print("\n📊 Current database status:")
            for table in required_tables:
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.scalar()
                print(f"   • {table}: {count} rows")
            
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization for Hitech Chatbot")
    parser.add_argument("--verify", action="store_true", help="Verify database setup")
    parser.add_argument("--init", action="store_true", help="Initialize database (default)")
    
    args = parser.parse_args()
    
    if args.verify:
        if verify_database():
            print("\n✅ Database verification passed!")
        else:
            print("\n❌ Database verification failed!")
            sys.exit(1)
    else:
        init_database()
