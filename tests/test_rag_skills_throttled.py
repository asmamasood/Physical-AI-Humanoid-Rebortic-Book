"""
Throttled test script for verifying unified RAG + Skills flow.
Includes sleeps to avoid hitting Gemini rate limits.
"""

import asyncio
import time
from backend.app.gemini_agent import get_gemini_agent

async def test_rag_with_skills_throttled():
    agent = get_gemini_agent()
    
    # Mock chunks
    chunks = [
        {
            "module": "module-1",
            "chapter": "chapter-1",
            "chunk_id": "chunk-123",
            "content": "Physical AI combines robotics and artificial intelligence to create intelligent moving systems.",
            "source_url": "http://example.com"
        }
    ]
    
    # Wait for cool down
    print("Waiting 15 seconds to ensure rate limit is cleared...")
    await asyncio.sleep(15)
    
    # Test 1: Standard RAG
    print("\n--- Test 1: Standard RAG ---")
    query1 = "What does Physical AI combine?"
    try:
        answer1, citations1 = await agent.generate_rag_answer(query1, chunks)
        print(f"Query: {query1}")
        print(f"Answer: {answer1}")
    except Exception as e:
        print(f"Test 1 Failed: {e}")
    
    # Wait between queries
    print("\nWaiting 30 seconds for next query...")
    await asyncio.sleep(30)
    
    # Test 2: Skill Trigger
    print("\n--- Test 2: Skill Trigger ---")
    query2 = "Summarize Module 1 Chapter 1 for me."
    try:
        answer2, citations2 = await agent.generate_rag_answer(query2, chunks)
        print(f"Query: {query2}")
        print(f"Answer: {answer2}")
    except Exception as e:
        print(f"Test 2 Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_rag_with_skills_throttled())
