"""
Pydantic models for RAG Chatboard API.

Defines request/response schemas for all endpoints.
"""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


# =============================================================================
# Chat Models
# =============================================================================

class Citation(BaseModel):
    """Citation reference to a source chunk."""
    module: str = Field(..., description="Module name (e.g., 'module-1')")
    chapter: str = Field(..., description="Chapter title")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    source_url: str = Field(..., description="URL to the source page")
    score: Optional[float] = Field(default=None, description="Relevance score from retrieval")


class ChatRequest(BaseModel):
    """Request body for /chat endpoint."""
    query: str = Field(..., min_length=1, max_length=2000, description="User's question")
    selected_text: Optional[str] = Field(default=None, description="Optional text selected/highlighted by user")
    module_id: Optional[str] = Field(default=None, description="Optional module identifier")
    chapter_id: Optional[str] = Field(default=None, description="Optional chapter identifier")
    book_id: Optional[str] = Field(default=None, description="Optional book identifier")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation tracking")
    user_id: Optional[str] = Field(default=None, description="User ID for history tracking")
    agent_id: Optional[int] = Field(default=None, description="Optional custom subagent ID")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")


class SelectiveChatRequest(BaseModel):
    """Request body for /selective-chat endpoint."""
    query: str = Field(..., min_length=1, max_length=2000, description="User's question about the selection")
    selection_text: str = Field(..., min_length=10, max_length=10000, description="User's highlighted text")
    selection_meta: Optional[dict] = Field(default=None, description="Optional metadata (url, element_id, etc.)")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation tracking")
    user_id: Optional[str] = Field(default=None, description="User ID for history tracking")


class ChatResponse(BaseModel):
    """Response body for chat endpoints."""
    answer: str = Field(..., description="Generated answer")
    citations: List[Citation] = Field(default_factory=list, description="Source citations")
    session_id: Optional[str] = Field(default=None, description="Session ID")


# =============================================================================
# Ingestion Models
# =============================================================================

class IngestRequest(BaseModel):
    """Request body for /ingest endpoint."""
    repo_path_or_url: Optional[str] = Field(
        default=None,
        description="Optional path to docs or git URL (uses default if not provided)"
    )
    force: bool = Field(default=False, description="Force re-ingestion of all content")


class IngestResponse(BaseModel):
    """Response body for /ingest endpoint."""
    status: str = Field(..., description="Ingestion status (completed, failed)")
    files_processed: int = Field(..., description="Number of files processed")
    chunks_created: int = Field(..., description="Number of chunks created")
    vectors_upserted: int = Field(..., description="Number of vectors upserted to Qdrant")
    duration_seconds: float = Field(..., description="Total duration in seconds")
    errors: List[str] = Field(default_factory=list, description="List of errors if any")


# =============================================================================
# Metadata Models
# =============================================================================

class MetaResponse(BaseModel):
    """Response body for /meta endpoint."""
    version: str = Field(..., description="API version")
    collection: str = Field(..., description="Qdrant collection name")
    vectors_count: int = Field(..., description="Number of vectors in collection")
    status: str = Field(..., description="Collection status")
    last_ingested: Optional[datetime] = Field(default=None, description="Last ingestion timestamp")


# =============================================================================
# Feedback Models
# =============================================================================

class FeedbackRequest(BaseModel):
    """Request body for /feedback endpoint."""
    session_id: str = Field(..., description="Session ID")
    message_id: str = Field(..., description="Message ID being rated")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    comment: Optional[str] = Field(default=None, max_length=1000, description="Optional feedback comment")


class FeedbackResponse(BaseModel):
    """Response body for /feedback endpoint."""
    status: str = Field(..., description="Feedback status (saved, failed)")
    feedback_id: Optional[str] = Field(default=None, description="Stored feedback ID")


# =============================================================================
# Error Models
# =============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")


# =============================================================================
# Health Models
# =============================================================================

class HealthResponse(BaseModel):
    """Response body for /health endpoint."""
    status: str = Field(..., description="Service status")
    version: str = Field(default="1.0.0", description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Server timestamp")


# =============================================================================
# Gamification & Agent Models
# =============================================================================

class UserProfileResponse(BaseModel):
    """User profile with points and level."""
    user_id: str
    points_total: int
    level: int
    created_at: datetime
    updated_at: datetime


class SubagentCreateRequest(BaseModel):
    """Request to create a new subagent."""
    name: str = Field(..., min_length=1, max_length=100)
    persona_description: str = Field(..., min_length=10, max_length=1000)
    skill_ids: List[int] = Field(default_factory=list)


class SubagentResponse(BaseModel):
    """Subagent information."""
    id: int
    user_id: str
    name: str
    persona_description: str
    skill_ids: List[int]
    created_at: datetime


class LeaderboardEntry(BaseModel):
    """Single entry in the leaderboard."""
    user_id: str
    points_total: int
    level: int


class LeaderboardResponse(BaseModel):
    """Ranked list of top users."""
    top_players: List[LeaderboardEntry]


# =============================================================================
# Profile & Personalization Models
# =============================================================================

class UserBackgroundRequest(BaseModel):
    """Request body for saving user background."""
    user_id: str = Field(..., description="User ID from Better Auth")
    software_role: str = Field(..., description="Software background role")
    software_level: str = Field(..., description="Beginner, Intermediate, Advanced")
    hardware_type: str = Field(..., description="Hardware setup type")
    gpu_available: bool = Field(default=False, description="Whether GPU is available")
    preferred_language: str = Field(default="en", description="en or ur")


class UserBackgroundResponse(BaseModel):
    """Response body for user background."""
    user_id: str
    software_role: Optional[str]
    software_level: Optional[str]
    hardware_type: Optional[str]
    gpu_available: bool
    preferred_language: str


class FullProfileResponse(BaseModel):
    """Combined profile including background info and gamification status."""
    background: UserBackgroundResponse
    status: UserProfileResponse


# =============================================================================
# Chat History Models
# =============================================================================

class ChatThread(BaseModel):
    """Conversation thread."""
    id: str
    user_id: str
    title: Optional[str]
    created_at: datetime


class ChatMessage(BaseModel):
    """Single message in a thread."""
    id: str
    thread_id: str
    role: str
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    """List of threads."""
    threads: List[ChatThread]
