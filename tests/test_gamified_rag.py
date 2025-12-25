"""
Integration test for Gamified Agents & Skills System.
"""

import asyncio
import logging
import uuid
from backend.app.db_neon import get_neon_db
from backend.app.gemini_agent import get_gemini_agent
from backend.app.gamification.points import points_manager
from backend.app.skills.registry import registry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_integration_test():
    user_id = f"test_user_{uuid.uuid4().hex[:8]}"
    logger.info(f"Starting integration test for user: {user_id}")
    
    db = get_neon_db()
    
    # 1. Initialize Profile
    profile = await points_manager.get_user_status(user_id)
    logger.info(f"Initial Profile: {profile}")
    
    # 2. Create a Subagent
    agent_id = await db.create_subagent(
        user_id=user_id,
        name="Tutor Bot",
        persona="A helpful robotics tutor",
        skill_ids=[]
    )
    await points_manager.award_points(user_id, "create_subagent")
    logger.info(f"Created Subagent ID: {agent_id}")
    
    profile_after_create = await points_manager.get_user_status(user_id)
    logger.info(f"Profile after creation (expected +50): {profile_after_create}")
    
    # 3. Test Smart Answer (Function Calling)
    agent = get_gemini_agent()
    
    # Query that should trigger 'summarize_chapter' skill
    query = "Can you summarize Module 1 Chapter 1 for me?"
    logger.info(f"Testing Smart Answer with query: {query}")
    
    answer = await agent.generate_smart_answer(query, user_id=user_id)
    logger.info(f"AI Response: {answer}")
    
    # 4. Verify Point Reward for Skill Use
    profile_after_skill = await points_manager.get_user_status(user_id)
    logger.info(f"Profile after skill use (expected +5): {profile_after_skill}")
    
    # 5. Check Leaderboard
    if db.enabled:
        await db.connect()
        async with db.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM user_profiles ORDER BY points_total DESC LIMIT 5")
            logger.info("Current Leaderboard:")
            for r in rows:
                logger.info(f" - {r['user_id']}: {r['points_total']} pts (Lvl {r['level']})")

if __name__ == "__main__":
    asyncio.run(run_integration_test())
