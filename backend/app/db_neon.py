"""
Neon Serverless Postgres client for RAG Chatboard.

Provides optional conversation history and feedback storage.
"""

import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from functools import lru_cache
import json
import uuid

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

from .config import get_settings


class NeonDB:
    """
    Async client for Neon Serverless Postgres.
    
    Provides optional storage for:
    - Conversation history
    - User feedback
    - Ingestion metadata
    """
    
    def __init__(self, connection_url: str = None):
        """
        Initialize Neon client.
        
        Args:
            connection_url: Neon connection URL (uses settings if not provided)
        """
        self.enabled = False
        self.pool = None
        
        if connection_url is None:
            settings = get_settings()
            connection_url = settings.neon_db_url
        
        self.connection_url = connection_url
        
        if connection_url and ASYNCPG_AVAILABLE:
            self.enabled = True
    
    async def connect(self):
        """Create connection pool."""
        if not self.enabled:
            return
        
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                self.connection_url,
                min_size=1,
                max_size=5
            )
    
    async def close(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def ensure_tables(self):
        """Create tables if they don't exist."""
        if not self.enabled:
            return
        
        await self.connect()
        
        async with self.pool.acquire() as conn:
            # Chat Threads for History
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_threads (
                    id UUID PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Chat Messages for History
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id UUID PRIMARY KEY,
                    thread_id UUID REFERENCES chat_threads(id) ON DELETE CASCADE,
                    role TEXT CHECK (role IN ('user', 'assistant')),
                    content TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Conversations table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255),
                    session_id VARCHAR(255) NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    citations JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add user_id column if it doesn't exist (migration)
            await conn.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='conversations' AND column_name='user_id') THEN
                        ALTER TABLE conversations ADD COLUMN user_id VARCHAR(255);
                    END IF;
                END $$;
            """)
            
            # Feedback table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    message_id VARCHAR(255) NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Ingestion metadata table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS ingestion_runs (
                    id SERIAL PRIMARY KEY,
                    files_processed INTEGER NOT NULL,
                    chunks_created INTEGER NOT NULL,
                    vectors_upserted INTEGER NOT NULL,
                    duration_seconds FLOAT NOT NULL,
                    errors JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # User profiles (Points & Levels)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id VARCHAR(255) PRIMARY KEY,
                    points_total INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Agent Skills (Modular logic definitions)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_skills (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    description TEXT NOT NULL,
                    points_value INTEGER DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # User Subagents (Custom AI personas)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_subagents (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    persona_description TEXT NOT NULL,
                    skill_ids INTEGER[] DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE
                )
            """)

            # Better Auth: users table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "user" (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    "emailVerified" BOOLEAN NOT NULL DEFAULT FALSE,
                    image TEXT,
                    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Better Auth: sessions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS session (
                    id TEXT PRIMARY KEY,
                    "expiresAt" TIMESTAMP NOT NULL,
                    token TEXT NOT NULL UNIQUE,
                    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    "ipAddress" TEXT,
                    "userAgent" TEXT,
                    "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE
                )
            """)

            # Better Auth: accounts table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS account (
                    id TEXT PRIMARY KEY,
                    "accountId" TEXT NOT NULL,
                    "providerId" TEXT NOT NULL,
                    "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    "accessToken" TEXT,
                    "refreshToken" TEXT,
                    "idToken" TEXT,
                    "accessTokenExpiresAt" TIMESTAMP,
                    "refreshTokenExpiresAt" TIMESTAMP,
                    scope TEXT,
                    password TEXT,
                    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Better Auth: verification table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS verification (
                    id TEXT PRIMARY KEY,
                    identifier TEXT NOT NULL,
                    value TEXT NOT NULL,
                    "expiresAt" TIMESTAMP NOT NULL,
                    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # User Background for personalization
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_background (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL UNIQUE,
                    software_role VARCHAR(50),
                    software_level VARCHAR(20),
                    hardware_type VARCHAR(50),
                    gpu_available BOOLEAN DEFAULT FALSE,
                    preferred_language VARCHAR(10) DEFAULT 'en',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migration for existing table
            await conn.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='user_background' AND column_name='preferred_language') THEN
                        ALTER TABLE user_background ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en';
                    END IF;
                END $$;
            """)

    
    async def save_conversation(
        self,
        session_id: str,
        query: str,
        response: str,
        citations: List[Dict[str, Any]],
        user_id: Optional[str] = None
    ) -> Optional[int]:
        """
        Save a conversation to the database.
        
        Returns the conversation ID if saved, None if disabled.
        """
        if not self.enabled:
            return None
        
        await self.connect()
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO conversations (session_id, query, response, citations, user_id)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """, session_id, query, response, json.dumps(citations), user_id)
            
            return row['id']

    async def get_chat_history(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent chat history for a user or session.
        """
        if not self.enabled:
            return []
        
        await self.connect()
        
        async with self.pool.acquire() as conn:
            if user_id:
                rows = await conn.fetch("""
                    SELECT query, response, created_at FROM conversations
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                """, user_id, limit)
            elif session_id:
                rows = await conn.fetch("""
                    SELECT query, response, created_at FROM conversations
                    WHERE session_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                """, session_id, limit)
            else:
                return []
            
            # Return in chronological order
            history = [dict(row) for row in rows]
            history.reverse()
            return history
            
    async def save_chat_interaction(
        self,
        thread_id: str,
        user_id: str,
        user_message: str,
        assistant_message: str,
        title: Optional[str] = None
    ) -> None:
        """Save a full interaction (User + Bot) to the new history tables."""
        if not self.enabled:
            return

        await self.connect()
        async with self.pool.acquire() as conn:
            # 1. Ensure Thread Exists
            await conn.execute("""
                INSERT INTO chat_threads (id, user_id, title)
                VALUES ($1, $2, $3)
                ON CONFLICT (id) DO NOTHING
            """, thread_id, user_id, title or user_message[:50])

            # 2. Save User Message
            await conn.execute("""
                INSERT INTO chat_messages (id, thread_id, role, content)
                VALUES ($1, $2, 'user', $3)
            """, str(uuid.uuid4()), thread_id, user_message)

            # 3. Save Assistant Message
            await conn.execute("""
                INSERT INTO chat_messages (id, thread_id, role, content)
                VALUES ($1, $2, 'assistant', $3)
            """, str(uuid.uuid4()), thread_id, assistant_message)
    
    async def save_feedback(
        self,
        session_id: str,
        message_id: str,
        rating: int,
        comment: Optional[str] = None
    ) -> Optional[int]:
        """
        Save user feedback to the database.
        
        Returns the feedback ID if saved, None if disabled.
        """
        if not self.enabled:
            return None
        
        await self.connect()
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO feedback (session_id, message_id, rating, comment)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, session_id, message_id, rating, comment)
            
            return row['id']
    
    async def save_ingestion_run(
        self,
        files_processed: int,
        chunks_created: int,
        vectors_upserted: int,
        duration_seconds: float,
        errors: List[str]
    ) -> Optional[int]:
        """
        Save ingestion run metadata.
        
        Returns the run ID if saved, None if disabled.
        """
        if not self.enabled:
            return None
        
        await self.connect()
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO ingestion_runs (files_processed, chunks_created, vectors_upserted, duration_seconds, errors)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """, files_processed, chunks_created, vectors_upserted, duration_seconds, json.dumps(errors))
            
            return row['id']
    
    async def get_last_ingestion(self) -> Optional[Dict[str, Any]]:
        """Get the last ingestion run metadata."""
        if not self.enabled:
            return None
        
        await self.connect()
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM ingestion_runs
                ORDER BY created_at DESC
                LIMIT 1
            """)
            
            if row:
                return dict(row)
            return None

    # =========================================================================
    # Gamification & Agents Helpers
    # =========================================================================

    async def get_or_create_profile(self, user_id: str) -> Dict[str, Any]:
        """Fetch user profile or create if not exists."""
        if not self.enabled:
            return {"user_id": user_id, "points_total": 0, "level": 1}
        
        await self.connect()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO user_profiles (user_id)
                VALUES ($1)
                ON CONFLICT (user_id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
                RETURNING *
            """, user_id)
            return dict(row)

    async def add_points(self, user_id: str, points: int) -> int:
        """Increment user points and return new total."""
        if not self.enabled:
            return 0
        
        await self.connect()
        async with self.pool.acquire() as conn:
            new_total = await conn.fetchval("""
                UPDATE user_profiles
                SET points_total = points_total + $2, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = $1
                RETURNING points_total
            """, user_id, points)
            
            # Simple level calc: 1 level per 100 points
            if new_total:
                new_level = (new_total // 100) + 1
                await conn.execute("UPDATE user_profiles SET level = $2 WHERE user_id = $1", user_id, new_level)
                return new_total
            return 0

    async def create_subagent(self, user_id: str, name: str, persona: str, skill_ids: List[int]) -> int:
        """Register a new custom subagent."""
        if not self.enabled:
            return 0
        
        await self.connect()
        async with self.pool.acquire() as conn:
            # First ensure profile exists
            await self.get_or_create_profile(user_id)
            
            row = await conn.fetchrow("""
                INSERT INTO user_subagents (user_id, name, persona_description, skill_ids)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, user_id, name, persona, skill_ids)
            return row['id']

    async def get_user_subagents(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch all subagents for a user."""
        if not self.enabled:
            return []
        
        await self.connect()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM user_subagents WHERE user_id = $1
            """, user_id)
            return [dict(r) for r in rows]

    async def get_subagent_full(self, agent_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a subagent with its associated skill details."""
        if not self.enabled:
            return None
        
        await self.connect()
        async with self.pool.acquire() as conn:
            # Fetch agent first
            agent_row = await conn.fetchrow("SELECT * FROM user_subagents WHERE id = $1", agent_id)
            if not agent_row:
                return None
            
            agent = dict(agent_row)
            skill_ids = agent.get('skill_ids', [])
            
            if skill_ids:
                # Fetch skills
                skill_rows = await conn.fetch("SELECT name, description FROM agent_skills WHERE id = ANY($1)", skill_ids)
                agent['skills'] = [dict(r) for r in skill_rows]
            else:
                agent['skills'] = []
                
            return agent

    async def register_skill(self, name: str, description: str, points_value: int = 10) -> int:
        """Internal helper to register a global skill definition."""
        if not self.enabled:
            return 0
        
        await self.connect()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO agent_skills (name, description, points_value)
                VALUES ($1, $2, $3)
                ON CONFLICT (name) DO UPDATE SET description = $2, points_value = $3
                RETURNING id
            """, name, description, points_value)
            return row['id']

    async def save_user_background(
        self,
        user_id: str,
        software_role: str,
        software_level: str,
        hardware_type: str,
        gpu_available: bool,
        preferred_language: str = 'en'
    ) -> Optional[int]:
        """Save or update user background for personalization."""
        if not self.enabled:
            return None
        
        await self.connect()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO user_background (user_id, software_role, software_level, hardware_type, gpu_available, preferred_language)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (user_id) DO UPDATE SET
                    software_role = $2,
                    software_level = $3,
                    hardware_type = $4,
                    gpu_available = $5,
                    preferred_language = $6,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, user_id, software_role, software_level, hardware_type, gpu_available, preferred_language)
            return row['id']

    async def get_user_background(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user background for personalization."""
        if not self.enabled:
            return None
        
        await self.connect()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM user_background WHERE user_id = $1
            """, user_id)
            return dict(row) if row else None



# Singleton instance
_neon_db: Optional[NeonDB] = None


def get_neon_db() -> NeonDB:
    """Get Neon DB instance (creates if needed)."""
    global _neon_db
    if _neon_db is None:
        _neon_db = NeonDB()
    return _neon_db
