import asyncio
from backend.app.gemini_agent import get_gemini_agent

async def test_baseline():
    print("Testing Baseline RAG stability...")
    agent = get_gemini_agent()
    
    mock_chunks = [
        {
            "module": "module-1",
            "chapter": "chapter-1",
            "chunk_id": "chunk-1",
            "content": "Physical AI is a branch of robotics that focuses on creating intelligent, physically embodied agents.",
            "source_url": "http://example.com"
        }
    ]
    
    try:
        query = "What is Physical AI?"
        print(f"Query: {query}")
        answer, citations = await agent.generate_rag_answer(query, mock_chunks)
        print(f"\nANSWER: {answer}")
        print(f"CITATIONS: {len(citations)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_baseline())
