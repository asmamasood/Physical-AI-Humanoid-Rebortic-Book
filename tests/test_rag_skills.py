"""
Test script for verifying unified RAG + Skills flow.
"""

import asyncio
from backend.app.gemini_agent import get_gemini_agent

async def test_rag_with_skills():
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
    
    # Test 1: Standard RAG (should use context)
    print("\n--- Test 1: Standard RAG ---")
    query1 = "What does Physical AI combine?"
    answer1, citations1 = await agent.generate_rag_answer(query1, chunks)
    print(f"Query: {query1}")
    print(f"Answer: {answer1}")
    print(f"Citations: {citations1}")
    
    # Test 2: Skill Trigger (should use summarize_chapter tool)
    print("\n--- Test 2: Skill Trigger ---")
    query2 = "Summarize Module 1 Chapter 1 for me."
    answer2, citations2 = await agent.generate_rag_answer(query2, chunks)
    print(f"Query: {query2}")
    print(f"Answer: {answer2}")
    print(f"Citations: {citations2}")

if __name__ == "__main__":
    asyncio.run(test_rag_with_skills())
