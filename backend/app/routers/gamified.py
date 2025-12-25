"""
Router for Gamified Agents & Skills System.

Handles profile management, subagent creation, and points tracking.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from ..models import (
    UserProfileResponse, 
    SubagentCreateRequest, 
    SubagentResponse,
    LeaderboardResponse,
    LeaderboardEntry
)
from ..db_neon import get_neon_db
from ..gamification.points import points_manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/skills", response_model=List[dict])
async def list_skills():
    """List all available AI skills."""
    db = get_neon_db()
    if not db.enabled:
        return []
    
    await db.connect()
    async with db.pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM agent_skills ORDER BY name ASC")
        return [dict(r) for r in rows]


@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def get_user_status(user_id: str):
    """Get current points and level for a user."""
    profile = await points_manager.get_user_status(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile


@router.post("/agents/create", response_model=SubagentResponse)
async def create_subagent(user_id: str, request: SubagentCreateRequest):
    """Create a custom AI subagent and earn points."""
    db = get_neon_db()
    
    agent_id = await db.create_subagent(
        user_id=user_id,
        name=request.name,
        persona=request.persona_description,
        skill_ids=request.skill_ids
    )
    
    # Award points for creation
    await points_manager.award_points(user_id, "create_subagent")
    
    # Fetch and return the created agent
    agents = await db.get_user_subagents(user_id)
    for a in agents:
        if a['id'] == agent_id:
            return a
            
    raise HTTPException(status_code=500, detail="Failed to create subagent")


@router.get("/agents/{user_id}", response_model=List[SubagentResponse])
async def list_subagents(user_id: str):
    """List all custom agents for a user."""
    db = get_neon_db()
    return await db.get_user_subagents(user_id)


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(limit: int = 10):
    """View top ranked users by points."""
    db = get_neon_db()
    if not db.enabled:
        return {"top_players": []}
        
    await db.connect()
    async with db.pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT user_id, points_total, level
            FROM user_profiles
            ORDER BY points_total DESC
            LIMIT $1
        """, limit)
        
        players = [LeaderboardEntry(**dict(r)) for r in rows]
        return {"top_players": players}
