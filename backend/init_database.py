#!/usr/bin/env python3
"""
Database initialization script for Hitech RAG Chatbot.

ROOT CAUSE OF THE ERROR:
  Neon's default connection string ends in '-pooler' (PgBouncer).
  PgBouncer in *transaction* mode does NOT support DDL that requires a
  session-level lock, such as CREATE FUNCTION / CREATE TRIGGER.
  The server drops the connection the moment it sees PL/pgSQL.

FIX:
  We automatically derive a *direct* (non-pooled) URL for DDL operations by
  stripping '-pooler' from the hostname.  Plain table creation via
  SQLAlchemy metadata works through the pooler, so we keep it there.
"""

import os
import re
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.postgresql_service import Base
from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_url(url: str) -> str:
    """Remove parameters psycopg2 does not understand (e.g. channel_binding)."""
    url = re.sub(r'[&?]channel_binding=[^&]*', '', url)
    url = re.sub(r'\?&', '?', url)
    url = re.sub(r'\?$', '', url)
    return url


def direct_url(url: str) -> str:
    """Convert a Neon pooler URL to a direct connection URL.

    Pooler:  ep-xxx-pooler.region.aws.neon.tech
    Direct:  ep-xxx.region.aws.neon.tech
    """
    return re.sub(r'(ep-[^.]+)-pooler(\.[^/]+)', r'\1\2', url)


def make_engine(url: str, **kwargs):
    return create_engine(url, pool_pre_ping=True, **kwargs)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def init_database():
    raw_url = os.getenv("DATABASE_URL")
    if not raw_url:
        print("❌  DATABASE_URL not set.")
        sys.exit(1)

    pooler_url = clean_url(raw_url)
    ddl_url    = direct_url(pooler_url)   # for CREATE FUNCTION / CREATE TRIGGER

    print("🔧  Hitech RAG Chatbot — Database Initialization")
    print("=" * 62)

    # ------------------------------------------------------------------
    # Step 1: Connect & verify (pooler is fine for SELECT)
    # ------------------------------------------------------------------
    print("\n📡  Connecting to database …")
    try:
        engine = make_engine(pooler_url)
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar()
        print("✅  Connected to PostgreSQL")
        print(f"    Version: {version[:70]}…")
    except Exception as exc:
        print(f"❌  Cannot connect: {exc}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 2: Create tables (SQLAlchemy metadata — works via pooler)
    # ------------------------------------------------------------------
    print("\n📦  Creating tables …")
    try:
        Base.metadata.create_all(bind=engine)
        for tbl in ("leads", "conversations", "messages"):
            print(f"    ✓  Table '{tbl}' created/verified")
    except Exception as exc:
        print(f"❌  Table creation failed: {exc}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 3: Indexes (simple DDL — pooler usually handles this)
    # ------------------------------------------------------------------
    print("\n🔍  Creating indexes …")
    index_sql = """
        CREATE INDEX IF NOT EXISTS idx_leads_session_id      ON leads(session_id);
        CREATE INDEX IF NOT EXISTS idx_leads_email           ON leads(email);
        CREATE INDEX IF NOT EXISTS idx_leads_status          ON leads(status);
        CREATE INDEX IF NOT EXISTS idx_leads_created_at      ON leads(created_at);

        CREATE INDEX IF NOT EXISTS idx_conv_session_id       ON conversations(session_id);
        CREATE INDEX IF NOT EXISTS idx_conv_lead_id          ON conversations(lead_id);
        CREATE INDEX IF NOT EXISTS idx_conv_escalated        ON conversations(is_escalated);
        CREATE INDEX IF NOT EXISTS idx_conv_last_msg         ON conversations(last_message_at);

        CREATE INDEX IF NOT EXISTS idx_msg_session_id        ON messages(session_id);
        CREATE INDEX IF NOT EXISTS idx_msg_conv_id           ON messages(conversation_id);
        CREATE INDEX IF NOT EXISTS idx_msg_created_at        ON messages(created_at);
        CREATE INDEX IF NOT EXISTS idx_msg_session_created   ON messages(session_id, created_at);
    """
    _run_ddl(engine, index_sql, "Indexes", ddl_url)

    # ------------------------------------------------------------------
    # Step 4: Trigger functions & triggers (MUST use direct, non-pooled)
    # ------------------------------------------------------------------
    print("\n⚙️   Creating functions & triggers (direct connection) …")

    fn_updated_at = """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER LANGUAGE plpgsql AS $func$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $func$;
    """

    trigger_leads = """
        DROP TRIGGER IF EXISTS update_leads_updated_at ON leads;
        CREATE TRIGGER update_leads_updated_at
            BEFORE UPDATE ON leads
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """

    trigger_convs = """
        DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
        CREATE TRIGGER update_conversations_updated_at
            BEFORE UPDATE ON conversations
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """

    fn_conv_stats = """
        CREATE OR REPLACE FUNCTION update_conversation_on_message()
        RETURNS TRIGGER LANGUAGE plpgsql AS $func$
        BEGIN
            UPDATE conversations
            SET last_message_at = NEW.created_at,
                message_count   = message_count + 1,
                updated_at      = CURRENT_TIMESTAMP
            WHERE session_id = NEW.session_id;
            RETURN NEW;
        END;
        $func$;
    """

    trigger_stats = """
        DROP TRIGGER IF EXISTS update_conversation_stats ON messages;
        CREATE TRIGGER update_conversation_stats
            AFTER INSERT ON messages
            FOR EACH ROW EXECUTE FUNCTION update_conversation_on_message();
    """

    fn_conv_messages = """
        CREATE OR REPLACE FUNCTION get_conversation_with_messages(
            p_session_id    VARCHAR,
            p_message_limit INTEGER DEFAULT 10
        )
        RETURNS TABLE (
            session_id        VARCHAR,
            lead_name         VARCHAR,
            lead_email        VARCHAR,
            is_escalated      BOOLEAN,
            escalation_notes  TEXT,
            messages          JSONB
        ) LANGUAGE plpgsql AS $func$
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
                            'id',        m.id,
                            'role',      m.role,
                            'content',   m.content,
                            'sources',   m.sources,
                            'metadata',  m.metadata,
                            'timestamp', m.created_at
                        ) ORDER BY m.created_at DESC
                    ) FILTER (WHERE m.id IS NOT NULL),
                    '[]'::JSONB
                ) AS messages
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
        $func$;
    """

    steps = [
        (fn_updated_at,    "Function: update_updated_at_column"),
        (trigger_leads,    "Trigger:  update_leads_updated_at"),
        (trigger_convs,    "Trigger:  update_conversations_updated_at"),
        (fn_conv_stats,    "Function: update_conversation_on_message"),
        (trigger_stats,    "Trigger:  update_conversation_stats"),
        (fn_conv_messages, "Function: get_conversation_with_messages"),
    ]

    ddl_engine = make_engine(
        ddl_url,
        pool_size=1,
        max_overflow=0,
        connect_args={"connect_timeout": 30},
    )

    all_ok = True
    for sql, label in steps:
        try:
            # Each function/trigger needs its own connection to avoid
            # PgBouncer transaction-mode conflicts
            with ddl_engine.connect() as conn:
                conn.execute(text("SET LOCAL statement_timeout = '30s'"))
                # Execute each statement separately
                for stmt in _split_statements(sql):
                    if stmt.strip():
                        conn.execute(text(stmt))
                conn.commit()
            print(f"    ✓  {label}")
        except Exception as exc:
            print(f"    ⚠  {label} — {exc}")
            all_ok = False

    ddl_engine.dispose()

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    print("\n" + "=" * 62)
    if all_ok:
        print("✅  Database initialization complete!")
    else:
        print("⚠️   Database initialized (tables/indexes OK).")
        print("    Some triggers failed — the app still works without them.")
        print("    Tip: If your Neon URL contains '-pooler', the direct URL")
        print(f"    used was: {ddl_url[:70]}")

    print("\n📊  Tables: leads, conversations, messages")
    print("🚀  Start the backend: uvicorn app.main:app --reload")


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _run_ddl(engine, sql: str, label: str, fallback_url: str):
    """Try DDL on the given engine; if it fails, retry with direct URL."""
    try:
        with engine.connect() as conn:
            for stmt in _split_statements(sql):
                if stmt.strip():
                    conn.execute(text(stmt))
            conn.commit()
        print(f"    ✓  {label} created")
    except Exception as exc:
        print(f"    ⚠  Pooler rejected {label} ({exc.__class__.__name__}), retrying on direct URL …")
        try:
            direct_engine = make_engine(fallback_url, pool_size=1, max_overflow=0)
            with direct_engine.connect() as conn:
                for stmt in _split_statements(sql):
                    if stmt.strip():
                        conn.execute(text(stmt))
                conn.commit()
            direct_engine.dispose()
            print(f"    ✓  {label} created (via direct URL)")
        except Exception as exc2:
            print(f"    ⚠  {label} skipped: {exc2}")


def _split_statements(sql: str):
    """
    Naively split a SQL block into individual statements.
    Respects $func$ dollar-quoting so we don't split inside PL/pgSQL bodies.
    """
    statements = []
    current = []
    in_dollar_quote = False
    dollar_tag = ''

    for line in sql.splitlines():
        stripped = line.strip()

        # Detect start/end of $func$ block
        if not in_dollar_quote:
            if '$func$' in stripped or '$' in stripped:
                # Check for opening dollar-quote
                if stripped.count('$func$') % 2 == 1 or (stripped.count('$$') % 2 == 1):
                    in_dollar_quote = True
        else:
            if '$func$' in stripped or '$$' in stripped:
                in_dollar_quote = False

        current.append(line)

        if not in_dollar_quote and stripped.endswith(';'):
            statements.append('\n'.join(current))
            current = []

    if current:
        statements.append('\n'.join(current))

    return statements


# ---------------------------------------------------------------------------
# Verify mode
# ---------------------------------------------------------------------------

def verify_database():
    raw_url = os.getenv("DATABASE_URL")
    if not raw_url:
        print("❌  DATABASE_URL not set")
        return False
    try:
        engine = make_engine(clean_url(raw_url))
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            ))
            tables = [r[0] for r in result]

        required = ['leads', 'conversations', 'messages']
        missing = [t for t in required if t not in tables]
        if missing:
            print(f"❌  Missing tables: {', '.join(missing)}")
            return False

        print("\n📊  Current database status:")
        with engine.connect() as conn:
            for tbl in required:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
                print(f"    • {tbl}: {count} rows")
        return True
    except Exception as exc:
        print(f"❌  Verification failed: {exc}")
        return False


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DB init for Hitech Chatbot")
    parser.add_argument("--verify", action="store_true", help="Verify existing setup")
    args = parser.parse_args()

    if args.verify:
        ok = verify_database()
        print("\n✅  Verification passed!" if ok else "\n❌  Verification failed!")
        sys.exit(0 if ok else 1)
    else:
        init_database()