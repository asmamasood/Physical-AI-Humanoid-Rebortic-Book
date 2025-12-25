"""
Gamification Point System for RAG Chatboard.

Handles logic for awarding points when users interact with skills,
subagents, or contribute to the platform.
"""

from typing import Optional
from ..db_neon import get_neon_db


class PointsManager:
    """
    Manages user points and level progression.
    """
    
    # Point values for different actions
    REWARDS = {
        "use_skill": 5,
        "create_subagent": 50,
        "ask_question": 2,
        "provide_feedback": 10
    }

    @staticmethod
    async def award_points(user_id: str, action: str) -> int:
        """
        Awards points to a user for a specific action.
        
        Args:
            user_id: The ID of the user.
            action: The action performed (must be in REWARDS).
            
        Returns:
            The new point total for the user.
        """
        if not user_id:
            return 0
            
        points = PointsManager.REWARDS.get(action, 0)
        if points == 0:
            return 0
            
        db = get_neon_db()
        new_total = await db.add_points(user_id, points)
        return new_total

    @staticmethod
    async def get_user_status(user_id: str) -> dict:
        """Fetch user points and level."""
        db = get_neon_db()
        return await db.get_or_create_profile(user_id)


# Singleton usage or instance
points_manager = PointsManager()
