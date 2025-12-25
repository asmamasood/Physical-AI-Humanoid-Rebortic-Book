"""
Isolated test for Skill Triggering.
"""

import asyncio
from backend.app.gemini_agent import get_gemini_agent

async def test_just_skill():
    agent = get_gemini_agent()
    query = "Summarize Module 1 Chapter 1 for me."
    print(f"Testing Query: {query}")
    
    # We pass empty chunks because the skill should be preferred by intent
    # or at least we want to see if it triggers.
    answer, citations = await agent.generate_rag_answer(query, [])
    
    print(f"\nFINAL ANSWER: {answer}")
    print(f"CITATIONS: {citations}")

if __name__ == "__main__":
    asyncio.run(test_just_skill())
